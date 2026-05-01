import json
from pathlib import Path

from ChatGPTAPI import create_file, call_gpt


SEMANTIC_MAP_PROMPT = """
You are a robotics perception and semantic reasoning module.

Inputs:
1. A 2D top-down semantic map image of a workspace
2. A task description for the robot

TASK:
{task_prompt}

Your job is to convert this into structured JSON, while interpreting the scene IN THE CONTEXT OF THE TASK.

Return ONLY valid JSON.

Schema:
{
  "scene_summary": "brief description",
  "zones": [
    {
      "id": "zone_1",
      "name": "wet area",
      "approx_location": "top-left | center | bottom-right | etc",
      "relative_size": "small | medium | large",
      "semantic_labels": ["hazard", "avoid", "safe", "goal_relevant", "irrelevant"],
      "task_relevance": "high | medium | low",
      "task_role": "must_avoid | neutral | preferred | goal_related"
    }
  ],
  "start": {"approx_location": "..."},
  "goal": {"approx_location": "..."},
  "task_interpretation": {
    "primary_objective": "...",
    "constraints": []
  }
}

Rules:
- Use the task to determine which regions matter.
- Do not include risk scores.
- Do not hallucinate objects not visible.
- Return JSON only.
"""


OPENVLA_STEERING_PROMPT = """
You are a robotics instruction-rewriting module.

Inputs:
1. Original robot task:
{task_prompt}

2. Scene semantic map JSON:
{semantic_map_json}

Rewrite the task into a concise instruction that can steer a vision-language-action policy.

Return ONLY valid JSON.

Schema:
{
  "original_task": "...",
  "rewritten_openvla_prompt": "...",
  "constraints": [],
  "important_objects": [
    {
      "object_id": "object_1",
      "name": "...",
      "role": "avoid | target | obstacle | contextual"
    }
  ],
  "reasoning_summary": "short explanation"
}

Rules:
- Preserve the original task goal.
- Add semantic safety constraints only if supported by the task or semantic map.
- Keep the rewritten prompt short and action-oriented.
- Return JSON only.
"""


def _ensure_dict(output):
    """Convert GPT output to dict if it comes back as a JSON string."""
    if isinstance(output, dict):
        return output
    if isinstance(output, str):
        return json.loads(output)
    raise TypeError(f"Expected dict or JSON string, got {type(output)}")


def save_json(path: str, data: dict) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def run_semantic_safety_pipeline(
    image_path: str,
    task_text: str,
    save_dir: str | None = None,
    verbose: bool = False,
) -> dict:
    """
    Run:
    image + task text -> semantic map -> rewritten OpenVLA prompt.

    Returns:
    {
      "semantic_map": dict,
      "steering_output": dict,
      "rewritten_openvla_prompt": str
    }
    """

    semantic_prompt = SEMANTIC_MAP_PROMPT.replace("{task_prompt}", task_text)

    image_file_id = create_file(image_path)

    semantic_map = call_gpt(semantic_prompt, image_file_id)
    semantic_map = _ensure_dict(semantic_map)

    openvla_prompt = OPENVLA_STEERING_PROMPT \
        .replace("{task_prompt}", task_text) \
        .replace("{semantic_map_json}", json.dumps(semantic_map, indent=2))

    steering_output = call_gpt(openvla_prompt, image_file_id)
    steering_output = _ensure_dict(steering_output)

    rewritten_prompt = steering_output.get("rewritten_openvla_prompt", task_text)

    result = {
        "semantic_map": semantic_map,
        "steering_output": steering_output,
        "rewritten_openvla_prompt": rewritten_prompt,
    }

    if save_dir is not None:
        save_json(f"{save_dir}/generated_semantic_map.json", semantic_map)
        save_json(f"{save_dir}/openvla_steering_prompt.json", steering_output)

    if verbose:
        print("Generated semantic map:")
        print(json.dumps(semantic_map, indent=2))
        print("\nGenerated OpenVLA steering prompt:")
        print(json.dumps(steering_output, indent=2))

    return result


def run_semantic_safety_pipeline_from_file(
    image_path: str,
    task_path: str,
    save_dir: str | None = None,
    verbose: bool = False,
) -> dict:
    with open(task_path, "r") as f:
        task_text = f.read().strip()

    return run_semantic_safety_pipeline(
        image_path=image_path,
        task_text=task_text,
        save_dir=save_dir,
        verbose=verbose,
    )