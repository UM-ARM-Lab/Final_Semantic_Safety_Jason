# environments.py
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon

planner_input = {
    "entity_id": "robot_1",
    "goal": ["move from start to goal safely"],
    "context": {
        "entities": {
            "world": {
                "type": "workspace",
                "bounds": {"xmin": 0.0, "ymin": 0.0, "xmax": 1.0, "ymax": 1.0},
            },

            # 1. Construction site (top middle)
            "construction": {
                "type": "zone",
                "name": "Construction Site",
                "bounds": {"xmin": 0.35, "ymin": 0.65, "xmax": 0.65, "ymax": 0.90},
                "semantic_entity": {
                    "type": "hazard",
                    "description": "Active construction with heavy machinery."
                },
            },

            # 2. Playground (top right)
            "playground": {
                "type": "zone",
                "name": "Playground",
                "bounds": {"xmin": 0.75, "ymin": 0.65, "xmax": 0.95, "ymax": 0.90},
                "semantic_entity": {
                    "type": "human_zone",
                    "description": "Children present, high safety priority."
                },
            },

            # 3. Wet area (left middle)
            "wet": {
                "type": "zone",
                "name": "Wet Area",
                "bounds": {"xmin": 0.10, "ymin": 0.40, "xmax": 0.30, "ymax": 0.60},
                "semantic_entity": {
                    "type": "surface_condition",
                    "description": "Slippery wet surface."
                },
            },

            # 4. Icy area (bottom right)
            "icy": {
                "type": "zone",
                "name": "Icy Area",
                "bounds": {"xmin": 0.65, "ymin": 0.10, "xmax": 0.90, "ymax": 0.35},
                "semantic_entity": {
                    "type": "surface_condition",
                    "description": "Extremely slippery icy surface."
                },
            },

            # 5. Restricted zone (center)
            "restricted": {
                "type": "zone",
                "name": "Restricted Zone",
                "bounds": {"xmin": 0.40, "ymin": 0.35, "xmax": 0.60, "ymax": 0.55},
                "semantic_entity": {
                    "type": "policy",
                    "description": "Area robot should avoid entering."
                },
            },

            "start": {"type": "point", "x": 0.05, "y": 0.05},
            "goal": {"type": "point", "x": 0.95, "y": 0.95},
        },
    },

    "candidates": [

        # 1. Straight diagonal (cuts through everything)
        {
            "id": "traj_1",
            "trajectory": {
                "time": [0,1,2,3,4],
                "states": [
                    {"x": 0.05, "y": 0.05},
                    {"x": 0.30, "y": 0.30},
                    {"x": 0.50, "y": 0.50},  # hits restricted
                    {"x": 0.70, "y": 0.70},  # hits construction
                    {"x": 0.95, "y": 0.95},
                ],
            },
            "semantics": [],
        },

        # 2. Bottom sweep (hits icy only)
        {
            "id": "traj_2",
            "trajectory": {
                "time": [0,1,2,3,4,5],
                "states": [
                    {"x": 0.05, "y": 0.05},
                    {"x": 0.40, "y": 0.05},
                    {"x": 0.70, "y": 0.10},  # icy
                    {"x": 0.85, "y": 0.25},
                    {"x": 0.90, "y": 0.60},
                    {"x": 0.95, "y": 0.95},
                ],
            },
            "semantics": [],
        },

        # 3. Left + top (touches wet + construction edge)
        {
            "id": "traj_3",
            "trajectory": {
                "time": [0,1,2,3,4,5],
                "states": [
                    {"x": 0.05, "y": 0.05},
                    {"x": 0.05, "y": 0.50},  # near wet
                    {"x": 0.10, "y": 0.70},
                    {"x": 0.40, "y": 0.92},  # near construction
                    {"x": 0.75, "y": 0.92},  # near playground
                    {"x": 0.95, "y": 0.95},
                ],
            },
            "semantics": [],
        },

        # 4. Safe but long wraparound (avoids everything)
        {
            "id": "traj_4",
            "trajectory": {
                "time": [0,1,2,3,4,5,6,7],
                "states": [
                    {"x": 0.05, "y": 0.05},
                    {"x": 0.05, "y": 0.30},
                    {"x": 0.05, "y": 0.60},
                    {"x": 0.05, "y": 0.90},
                    {"x": 0.30, "y": 0.98},
                    {"x": 0.60, "y": 0.98},
                    {"x": 0.85, "y": 0.97},
                    {"x": 0.95, "y": 0.95},
                ],
            },
            "semantics": [],
        },

        # 5. Middle-right compromise (avoids restricted, hits playground edge)
        {
            "id": "traj_5",
            "trajectory": {
                "time": [0,1,2,3,4,5],
                "states": [
                    {"x": 0.05, "y": 0.05},
                    {"x": 0.30, "y": 0.20},
                    {"x": 0.60, "y": 0.40},
                    {"x": 0.80, "y": 0.70},  # playground edge
                    {"x": 0.90, "y": 0.85},
                    {"x": 0.95, "y": 0.95},
                ],
            },
            "semantics": [],
        },
    ],
}

def plot_environment(context: dict, candidates: list | None = None):
    fig, ax = plt.subplots(figsize=(6, 6))

    entities = context["entities"]

    # ---------------------------
    # ROOM BOUNDARY
    # ---------------------------
    bounds = entities["world"]["bounds"]
    xmin = bounds["xmin"]
    ymin = bounds["ymin"]
    xmax = bounds["xmax"]
    ymax = bounds["ymax"]

    room = Rectangle((xmin, ymin), xmax - xmin, ymax - ymin,
                     fill=False, linewidth=2)
    ax.add_patch(room)

    # ---------------------------
    # ZONES
    # ---------------------------
    for name, entity in entities.items():
        if entity["type"] == "zone":
            b = entity["bounds"]
            width = b["xmax"] - b["xmin"]
            height = b["ymax"] - b["ymin"]

            color_map = {
                "wet area": "blue",
                "very icy": "cyan",
                "icy": "cyan",
                "wet": "blue",
                "construction": "yellow",
                "playground": "green",
                "restricted": "red",
                "car crash": "red",
            }
            color = color_map.get(name, "gray")

            zone_rect = Rectangle(
                (b["xmin"], b["ymin"]),
                width,
                height,
                alpha=0.3,
                color=color
            )
            ax.add_patch(zone_rect)

            cx = b["xmin"] + width / 2
            cy = b["ymin"] + height / 2
            desc = entity.get("semantic_entity", {}).get("description", "")

            ax.text(
                cx, cy,
                f"{name}\n{desc}",
                ha="center", va="center"
            )

    # ---------------------------
    # START & GOAL
    # ---------------------------
    start = entities["start"]
    goal = entities["goal"]

    ax.scatter(start["x"], start["y"], s=100)
    ax.text(start["x"], start["y"], "Start", va="bottom")

    ax.scatter(goal["x"], goal["y"], s=100)
    ax.text(goal["x"], goal["y"], "Goal", va="bottom")

    # ---------------------------
    # TRAJECTORIES
    # ---------------------------
    if candidates is not None:
        for candidate in candidates:
            xs = [state["x"] for state in candidate["trajectory"]["states"]]
            ys = [state["y"] for state in candidate["trajectory"]["states"]]
            ax.plot(xs, ys, marker="o", label=candidate["id"])

    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_aspect("equal")
    ax.grid(False)
    ax.axis("off")

    ax.legend(loc="center left", bbox_to_anchor=(1, 0.5))

    plt.title("2D Semantic Environment")
    plt.savefig("current_test_map.png", bbox_inches="tight")
    plt.show()

from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt

def plot_generated_semantic_map(semantic_map: dict, save_path="generated_semantic_map_render.png"):
    fig, ax = plt.subplots(figsize=(6, 6))

    # generic normalized workspace
    ax.add_patch(Rectangle((0, 0), 1, 1, fill=False, linewidth=2))

    # rough placement map
    locations = {
        "top-left": (0.15, 0.75),
        "top-right": (0.65, 0.75),
        "bottom-left": (0.15, 0.15),
        "bottom-right": (0.65, 0.15),
        "center": (0.4, 0.4),
        "left": (0.1, 0.4),
        "right": (0.7, 0.4),
        "top": (0.4, 0.75),
        "bottom": (0.4, 0.1),
    }

    color_map = {
        "must_avoid": "red",
        "goal_related": "green",
        "preferred": "blue",
        "neutral": "gray",
    }

    for i, zone in enumerate(semantic_map.get("zones", [])):
        loc = zone.get("approx_location", "center")
        x, y = locations.get(loc, locations["center"])

        w, h = 0.25, 0.18
        task_role = zone.get("task_role", "neutral")
        color = color_map.get(task_role, "gray")

        rect = Rectangle((x, y), w, h, alpha=0.35, color=color)
        ax.add_patch(rect)

        label = zone.get("name", f"zone_{i+1}")
        role = zone.get("task_role", "")
        ax.text(x + w/2, y + h/2, f"{label}\n{role}", ha="center", va="center")

    # Start / Goal
    for key, marker_text in [("start", "Start"), ("goal", "Goal")]:
        loc = semantic_map.get(key, {}).get("approx_location", "center")
        x, y = locations.get(loc, locations["center"])
        ax.scatter(x + 0.1, y + 0.1, s=100)
        ax.text(x + 0.1, y + 0.12, marker_text, ha="center")

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect("equal")
    ax.axis("off")
    plt.title("Generated 2D Semantic Map")
    plt.savefig(save_path, bbox_inches="tight", dpi=200)
    #plt.show()
