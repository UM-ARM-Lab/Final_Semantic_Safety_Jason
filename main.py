import json
import requests

from environments import plot_generated_semantic_map
from Classes import PlannerInput
#from Prompt import build_prompt
from ChatGPTAPI import create_file, call_gpt 

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.1:8b"

#***********************\testing LLM/***************************************

def call_ollama(prompt: str) -> dict:
    """Call Ollama and return parsed JSON object (raises with helpful debug on failure)."""
    resp = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.1:8b",
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0
            }
        },
        timeout=120
    )
    resp.raise_for_status()
    payload = resp.json()

    if "response" not in payload:
        raise RuntimeError(f"Ollama response missing 'response' field: {payload}")

    text = payload["response"].strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        # incase oopsie
        raise RuntimeError(
            "Model did not return valid JSON.\n"
            f"Raw output:\n{text}\n"
            f"JSON error: {e}"
        )

def save_json(path: str, data: dict) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":

    SEMANTIC_MAP_PROMPT = """
    You are a robotics perception and semantic reasoning module.

    Inputs:
    1. A 2D top-down semantic map image of a workspace
    2. A task description for the robot

    TASK:
    {task_prompt}

    The image shows:
    - A rectangular room (workspace boundary)
    - Colored rectangular zones representing semantic regions
    - A Start point and a Goal point
    - (Possibly) candidate trajectories

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

        "semantic_labels": [
            "hazard",
            "avoid",
            "safe",
            "goal_relevant",
            "irrelevant"
        ],

        "task_relevance": "high | medium | low",
        "task_role": "must_avoid | neutral | preferred | goal_related"
        }
    ],

    "start": {
        "approx_location": "..."
    },

    "goal": {
        "approx_location": "..."
    },

    "task_interpretation": {
        "primary_objective": "...",
        "constraints": [
        "avoid wet areas",
        "stay out of restricted zones"
        ]
    }
    }

    Color semantics:
    - Blue: wet / slippery
    - Cyan: icy / very slippery
    - Yellow: construction / caution
    - Green: safe / low risk
    - Red: restricted / dangerous / must avoid

    Rules:
    - Use the TASK to determine:
    - which zones are important
    - which zones should be avoided
    - DO NOT include numeric coordinates
    - Use only coarse spatial descriptions
    - Do NOT hallucinate objects not visible
    - If a zone is irrelevant to the task, label it as "irrelevant"
    - Return JSON only
    """

    OPENVLA_STEERING_PROMPT = """
    You are a robotics instruction-rewriting module.

    Inputs:
    1. Original robot task:
    {task_prompt}

    2. Scene semantic map JSON:
    {semantic_map_json}

    Your job is to rewrite the task into a concise instruction that can steer a vision-language-action policy.

    Return ONLY valid JSON.

    Schema:
    {
    "original_task": "...",
    "rewritten_openvla_prompt": "...",
    "constraints": [
        "avoid the ramekin",
        "keep gripper away from fragile objects"
    ],
    "important_objects": [
        {
        "object_id": "object_1",
        "name": "ramekin",
        "role": "avoid | target | obstacle | contextual"
        }
    ],
    "reasoning_summary": "short explanation"
    }

    Rules:
    - The rewritten prompt should be short, direct, and action-oriented.
    - Preserve the original task goal.
    - Add semantic safety constraints only if supported by the task or semantic map.
    - Do not over-specify exact coordinates.
    - Do not include hidden reasoning.
    - Return JSON only.
    """

    bird_eye_image_filepath = "/home/jasonzou/Documents/openvla/experiments/env_images/libero_spatial_temp_task0_birdview.png"
    task_description_filepath = "/home/jasonzou/Documents/openvla/experiments/env_images/libero_spatial_temp_task0_task.txt"

    with open(task_description_filepath, "r") as f:
        task_prompt = f.read().strip()

    semantic_prompt = SEMANTIC_MAP_PROMPT.replace("{task_prompt}", task_prompt)

    bird_eye_file_id = create_file(bird_eye_image_filepath)

    generate_semantic_map = call_gpt(semantic_prompt, bird_eye_file_id)
    print("Generated semantic map:")
    print(generate_semantic_map)
    save_json("generated_semantic_map.json", generate_semantic_map)

    openvla_prompt = OPENVLA_STEERING_PROMPT \
        .replace("{task_prompt}", task_prompt) \
        .replace("{semantic_map_json}", json.dumps(generate_semantic_map, indent=2))

    gpt_out = call_gpt(openvla_prompt, bird_eye_file_id)
    print("Generated OpenVLA steering prompt:")
    print(gpt_out)
    save_json("openvla_steering_prompt.json", gpt_out)

    # plot_generated_semantic_map(
    # generate_semantic_map,
    # "/home/jasonzou/Documents/Semantic_Safety/generated_semantic_map_render.png"
    # )

    #save_json("current_test_GPT4.1mini.json", gpt_out)


#     # push data
#     pi = PlannerInput.from_dict(planner_input)
#     print("Loaded entity_id:", pi.entity_id,"\n")
#     print("Goal:", pi.goal.goal,"\n")
#     print("Candidates:", [c.id for c in pi.candidates], "\n")

#     prompt = build_prompt(planner_input)
#     llm_out = call_ollama(prompt)

#     print("LLM output:", llm_out, "\n")

#     save_json("planner_input_used.json", planner_input)
#     save_json("planner_output.json", llm_out)
