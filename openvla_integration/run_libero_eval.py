"""
run_libero_eval.py

Runs a model in a LIBERO simulation environment.

Usage:
    # OpenVLA:
    # IMPORTANT: Set `center_crop=True` if model is fine-tuned with augmentations
    python experiments/robot/libero/run_libero_eval.py \
        --model_family openvla \
        --pretrained_checkpoint <CHECKPOINT_PATH> \
        --task_suite_name [ libero_spatial | libero_object | libero_goal | libero_10 | libero_90 ] \
        --center_crop [ True | False ] \
        --run_id_note <OPTIONAL TAG TO INSERT INTO RUN ID FOR LOGGING> \
        --use_wandb [ True | False ] \
        --wandb_project <PROJECT> \
        --wandb_entity <ENTITY>
"""

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union
from LIBERO_PRO import perturbation
import yaml
from PIL import Image

import draccus
import numpy as np
import tqdm
#from libero.libero import benchmark
from libero.libero import benchmark, set_libero_default_path, get_libero_path

import wandb

# Append current directory so that interpreter can find experiments.robot
sys.path.append("../..")
from experiments.robot.libero.libero_utils import (
    get_libero_dummy_action,
    get_libero_env,
    get_libero_image,
    quat2axisangle,
    save_rollout_video,
)
from experiments.robot.openvla_utils import get_processor
from experiments.robot.robot_utils import (
    DATE_TIME,
    get_action,
    get_image_resize_size,
    get_model,
    invert_gripper_action,
    normalize_gripper_action,
    set_seed_everywhere,
)


@dataclass
class GenerateConfig:

    evaluation_config_path: str = "./experiments/robot/libero/LIBERO_PRO/evaluation_config.yaml"

    # fmt: off

    #################################################################################################################
    # Model-specific parameters
    #################################################################################################################
    model_family: str = "openvla"                    # Model family
    pretrained_checkpoint: Union[str, Path] = ""     # Pretrained checkpoint path
    load_in_8bit: bool = False                       # (For OpenVLA only) Load with 8-bit quantization
    load_in_4bit: bool = False                       # (For OpenVLA only) Load with 4-bit quantization

    center_crop: bool = True                         # Center crop? (if trained w/ random crop image aug)

    #################################################################################################################
    # LIBERO environment-specific parameters
    #################################################################################################################
    task_suite_name: str = "libero_spatial"          # Task suite. Options: libero_spatial, libero_object, libero_goal, libero_10, libero_90
    num_steps_wait: int = 10                         # Number of steps to wait for objects to stabilize in sim
    num_trials_per_task: int = 50                    # Number of rollouts per task

    #################################################################################################################
    # Utils
    #################################################################################################################
    run_id_note: Optional[str] = None                # Extra note to add in run ID for logging
    local_log_dir: str = "./experiments/logs"        # Local directory for eval logs

    use_wandb: bool = False                          # Whether to also log results in Weights & Biases
    wandb_project: str = "YOUR_WANDB_PROJECT"        # Name of W&B project to log to (use default!)
    wandb_entity: str = "YOUR_WANDB_ENTITY"          # Name of entity to log under

    seed: int = 7                                    # Random Seed (for reproducibility)

    # fmt: on


@draccus.wrap()
def eval_libero(cfg: GenerateConfig) -> None:
    assert cfg.pretrained_checkpoint is not None, "cfg.pretrained_checkpoint must not be None!"
    if "image_aug" in cfg.pretrained_checkpoint:
        assert cfg.center_crop, "Expecting `center_crop==True` because model was trained with image augmentations!"
    assert not (cfg.load_in_8bit and cfg.load_in_4bit), "Cannot use both 8-bit and 4-bit quantization!"

    # Set random seed
    set_seed_everywhere(cfg.seed)
    # Force LIBERO to use the real benchmark root, not any stale PRO root
    set_libero_default_path("/home/jasonzou/Documents/LIBERO/libero/libero")
    print("FORCED LIBERO ROOT:", get_libero_path("benchmark_root"))
    print("FORCED LIBERO INIT PATH:", get_libero_path("init_states"))
    print("FORCED LIBERO BDDL PATH:", get_libero_path("bddl_files"))

    # [OpenVLA] Set action un-normalization key
    cfg.unnorm_key = cfg.task_suite_name

    # Load model
    model = get_model(cfg)

    # [OpenVLA] Check that the model contains the action un-normalization key
    if cfg.model_family == "openvla":
        # In some cases, the key must be manually modified (e.g. after training on a modified version of the dataset
        # with the suffix "_no_noops" in the dataset name)
        if cfg.unnorm_key not in model.norm_stats and f"{cfg.unnorm_key}_no_noops" in model.norm_stats:
            cfg.unnorm_key = f"{cfg.unnorm_key}_no_noops"
        assert cfg.unnorm_key in model.norm_stats, f"Action un-norm key {cfg.unnorm_key} not found in VLA `norm_stats`!"

    # [OpenVLA] Get Hugging Face processor
    processor = None
    if cfg.model_family == "openvla":
        processor = get_processor(cfg)

    # Initialize local logging
    run_id = f"EVAL-{cfg.task_suite_name}-{cfg.model_family}-{DATE_TIME}"
    if cfg.run_id_note is not None:
        run_id += f"--{cfg.run_id_note}"
    os.makedirs(cfg.local_log_dir, exist_ok=True)
    local_log_filepath = os.path.join(cfg.local_log_dir, run_id + ".txt")
    log_file = open(local_log_filepath, "w")
    print(f"Logging to local log file: {local_log_filepath}")

    # Initialize Weights & Biases logging as well
    if cfg.use_wandb:
        wandb.init(
            entity=cfg.wandb_entity,
            project=cfg.wandb_project,
            name=run_id,
        )

    # Initialize LIBERO task suite
    # benchmark_dict = benchmark.get_benchmark_dict()
    # task_suite = benchmark_dict[cfg.task_suite_name]()
        # Initialize LIBERO task suite
    benchmark_dict = benchmark.get_benchmark_dict()

    # ---------------- LIBERO-PRO PATCH ----------------
    with open(cfg.evaluation_config_path, "r", encoding="utf-8") as f:
        evaluation_cfg = yaml.safe_load(f)

    evaluation_cfg["bddl_files_path"] = evaluation_cfg.get("bddl_files_path", "") + cfg.task_suite_name
    evaluation_cfg["task_suite_name"] = cfg.task_suite_name

    use_swap = evaluation_cfg.get("use_swap", False)
    use_object = evaluation_cfg.get("use_object", False)
    use_language = evaluation_cfg.get("use_language", False)
    use_task = evaluation_cfg.get("use_task", False)
    use_environment = evaluation_cfg.get("use_environment", False)

    print("PRO flags:", {
    "use_swap": use_swap,
    "use_object": use_object,
    "use_language": use_language,
    "use_task": use_task,
    "use_environment": use_environment,
    })

    num_flags = sum([use_swap, use_object, use_language, use_task, use_environment])

    if num_flags > 1:
        bddl_file_path = evaluation_cfg.get("bddl_files_path", "") + "_temp/"
        init_file_path = evaluation_cfg.get("init_file_dir", "") + cfg.task_suite_name + "_temp/"

        if not os.path.exists(bddl_file_path) or not os.path.exists(init_file_path):
            os.makedirs(init_file_path, exist_ok=True)
            os.makedirs(bddl_file_path, exist_ok=True)

            log_content = f"{use_swap},{use_object},{use_language},{use_task},{use_environment}"
            # with open(os.path.join(bddl_file_path, "log.txt"), "w") as log_file:
            #     log_file.write(log_content)
            # with open(os.path.join(bddl_file_path, "log.txt"), "w") as perturb_log_file:
            #     perturb_log_file.write(log_content)
            with open(os.path.join(bddl_file_path, "log.txt"), "w") as perturb_log_file:
                perturb_log_file.write(expected_log)

            perturbation.create_env(configs=evaluation_cfg)
        else:
            # with open(os.path.join(bddl_file_path, "log.txt"), "r") as log_file:
            #     log_contents = log_file.read().strip()
            with open(os.path.join(bddl_file_path, "log.txt"), "r") as perturb_log_file:
                log_contents = perturb_log_file.read().strip()

            expected_log = f"{use_swap},{use_object},{use_language},{use_task},{use_environment}"

            if log_contents != expected_log:
                for folder in [bddl_file_path, init_file_path]:
                    for root, dirs, files in os.walk(folder, topdown=False):
                        for name in files:
                            os.remove(os.path.join(root, name))
                        for name in dirs:
                            os.rmdir(os.path.join(root, name))

                os.makedirs(init_file_path, exist_ok=True)
                os.makedirs(bddl_file_path, exist_ok=True)

                with open(os.path.join(bddl_file_path, "log.txt"), "w") as log_file:
                    log_file.write(expected_log)

                perturbation.create_env(configs=evaluation_cfg)

        cfg.task_suite_name = cfg.task_suite_name + "_temp"

    elif num_flags == 1:
        if use_swap:
            perturb_key = "use_swap"
        elif use_object:
            perturb_key = "use_object"
        elif use_language:
            perturb_key = "use_language"
        elif use_task:
            perturb_key = "use_task"
        else:
            perturb_key = "use_environment"

        suffix = evaluation_cfg.get("perturbation_mapping", {}).get(perturb_key, "")
        init_file_path = evaluation_cfg.get("init_file_dir", "") + cfg.task_suite_name + "_" + suffix

        if not os.path.exists(init_file_path):
            perturbation.create_env(configs=evaluation_cfg)

        #cfg.task_suite_name = cfg.task_suite_name + "_" + suffix
        cfg.task_suite_name = cfg.task_suite_name + "_temp"
    # -------------- END LIBERO-PRO PATCH --------------

    benchmark_lookup_name = cfg.task_suite_name

    # PRO suites are based on the original suite definitions
    for suffix in ["_swap", "_object", "_lan", "_task", "_env", "_temp"]:
        if benchmark_lookup_name.endswith(suffix):
            benchmark_lookup_name = benchmark_lookup_name[: -len(suffix)]
            break

    print("Final cfg.task_suite_name:", cfg.task_suite_name)
    print("Benchmark lookup name:", benchmark_lookup_name)
    #task_suite = benchmark_dict[cfg.task_suite_name]()
    task_suite = benchmark_dict[benchmark_lookup_name]()
    
    num_tasks_in_suite = task_suite.n_tasks
    print(f"Task suite: {cfg.task_suite_name}")
    log_file.write(f"Task suite: {cfg.task_suite_name}\n")

    # Get expected image dimensions
    resize_size = get_image_resize_size(cfg)

    # Start evaluation
    total_episodes, total_successes = 0, 0
    for task_id in tqdm.tqdm(range(num_tasks_in_suite)):
        # Get task
        task = task_suite.get_task(task_id)
        print("About to load init states for suite:", cfg.task_suite_name)
        print("Benchmark lookup name:", benchmark_lookup_name)
        # Get default LIBERO initial states
        initial_states = task_suite.get_task_init_states(task_id)

        print("Initial states source sample shape/type:", type(initial_states), len(initial_states))
        print("Running suite name:", cfg.task_suite_name)
        print("Benchmark lookup name:", benchmark_lookup_name)

        # Initialize LIBERO environment and task description
        env, task_description = get_libero_env(task, cfg.model_family, resolution=256)

        # Start episodes
        task_episodes, task_successes = 0, 0
        for episode_idx in tqdm.tqdm(range(cfg.num_trials_per_task)):
            print(f"\nTask: {task_description}")
            log_file.write(f"\nTask: {task_description}\n")

            # Reset environment
            env.reset()

            # Set initial states
            obs = env.set_init_state(initial_states[episode_idx])

            # Save bird's-eye view image for semantic planner input
            if episode_idx == 0:  # save only first episode per task
                debug_img_dir = "./experiments/env_images"
                os.makedirs(debug_img_dir, exist_ok=True)

                bird_img = env.sim.render(
                    camera_name="birdview",
                    width=512,
                    height=512,
                    depth=False,
                )

                # robosuite images are often upside-down from sim.render
                bird_img = bird_img[::-1]

                img_path = os.path.join(
                    debug_img_dir,
                    f"{cfg.task_suite_name}_task{task_id}_birdview.png"
                )

                Image.fromarray(bird_img).save(img_path)
                print(f"Saved birdview image to: {img_path}")

            # Setup
            t = 0
            replay_images = []

            task_txt_path = os.path.join(
                debug_img_dir,
                f"{cfg.task_suite_name}_task{task_id}_task.txt"
            )

            with open(task_txt_path, "w") as f:
                f.write(task_description)

            print(f"Saved task text to: {task_txt_path}")

            # if cfg.task_suite_name == "libero_spatial":
            #     max_steps = 220  # longest training demo has 193 steps
            # elif cfg.task_suite_name == "libero_object":
            #     max_steps = 280  # longest training demo has 254 steps
            # elif cfg.task_suite_name == "libero_goal":
            #     max_steps = 300  # longest training demo has 270 steps
            # elif cfg.task_suite_name == "libero_10":
            #     max_steps = 520  # longest training demo has 505 steps
            # elif cfg.task_suite_name == "libero_90":
            #     max_steps = 400  # longest training demo has 373 steps

            suite_name_for_steps = cfg.task_suite_name
            for suffix in ["_swap", "_object", "_lan", "_task", "_env", "_temp"]:
                if suite_name_for_steps.endswith(suffix):
                    suite_name_for_steps = suite_name_for_steps[:-len(suffix)]
                    break

            if suite_name_for_steps == "libero_spatial":
                max_steps = 220
            elif suite_name_for_steps == "libero_object":
                max_steps = 280
            elif suite_name_for_steps == "libero_goal":
                max_steps = 300
            elif suite_name_for_steps == "libero_10":
                max_steps = 520
            elif suite_name_for_steps == "libero_90":
                max_steps = 400
            else:
                raise ValueError(f"Unknown task suite name: {cfg.task_suite_name}")

            print(f"Starting episode {task_episodes+1}...")
            log_file.write(f"Starting episode {task_episodes+1}...\n")
            while t < max_steps + cfg.num_steps_wait:
                try:
                    # IMPORTANT: Do nothing for the first few timesteps because the simulator drops objects
                    # and we need to wait for them to fall
                    if t < cfg.num_steps_wait:
                        obs, reward, done, info = env.step(get_libero_dummy_action(cfg.model_family))
                        t += 1
                        continue

                    # Get preprocessed image
                    img = get_libero_image(obs, resize_size)

                    # Save preprocessed image for replay video
                    replay_images.append(img)

                    # Prepare observations dict
                    # Note: OpenVLA does not take proprio state as input
                    observation = {
                        "full_image": img,
                        "state": np.concatenate(
                            (obs["robot0_eef_pos"], quat2axisangle(obs["robot0_eef_quat"]), obs["robot0_gripper_qpos"])
                        ),
                    }

                    # Query model to get action
                    action = get_action(
                        cfg,
                        model,
                        observation,
                        task_description,
                        processor=processor,
                    )

                    # Normalize gripper action [0,1] -> [-1,+1] because the environment expects the latter
                    action = normalize_gripper_action(action, binarize=True)

                    # [OpenVLA] The dataloader flips the sign of the gripper action to align with other datasets
                    # (0 = close, 1 = open), so flip it back (-1 = open, +1 = close) before executing the action
                    if cfg.model_family == "openvla":
                        action = invert_gripper_action(action)

                    # Execute action in environment
                    obs, reward, done, info = env.step(action.tolist())
                    if done:
                        task_successes += 1
                        total_successes += 1
                        break
                    t += 1

                except Exception as e:
                    print(f"Caught exception: {e}")
                    log_file.write(f"Caught exception: {e}\n")
                    break

            task_episodes += 1
            total_episodes += 1

            # Save a replay video of the episode
            save_rollout_video(
                replay_images, total_episodes, success=done, task_description=task_description, log_file=log_file
            )

            # Log current results
            print(f"Success: {done}")
            print(f"# episodes completed so far: {total_episodes}")
            print(f"# successes: {total_successes} ({total_successes / total_episodes * 100:.1f}%)")
            log_file.write(f"Success: {done}\n")
            log_file.write(f"# episodes completed so far: {total_episodes}\n")
            log_file.write(f"# successes: {total_successes} ({total_successes / total_episodes * 100:.1f}%)\n")
            log_file.flush()

        # Log final results
        print(f"Current task success rate: {float(task_successes) / float(task_episodes)}")
        print(f"Current total success rate: {float(total_successes) / float(total_episodes)}")
        log_file.write(f"Current task success rate: {float(task_successes) / float(task_episodes)}\n")
        log_file.write(f"Current total success rate: {float(total_successes) / float(total_episodes)}\n")
        log_file.flush()
        if cfg.use_wandb:
            wandb.log(
                {
                    f"success_rate/{task_description}": float(task_successes) / float(task_episodes),
                    f"num_episodes/{task_description}": task_episodes,
                }
            )

    # Save local log file
    log_file.close()

    # Push total metrics and local log file to wandb
    if cfg.use_wandb:
        wandb.log(
            {
                "success_rate/total": float(total_successes) / float(total_episodes),
                "num_episodes/total": total_episodes,
            }
        )
        wandb.save(local_log_filepath)


if __name__ == "__main__":
    eval_libero()
