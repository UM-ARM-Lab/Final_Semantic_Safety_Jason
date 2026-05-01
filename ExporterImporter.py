import json
from pathlib import Path
from Classes import PlannerInput

def load_planner_input_json(path: str) -> PlannerInput:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"JSON file not found: {p.resolve()}")

    with p.open("r", encoding="utf-8") as f:
        data = json.load(f)

    required = ["entity_id", "goal", "context", "candidates"]
    missing = [k for k in required if k not in data]
    if missing:
        raise ValueError(f"Missing required keys in JSON: {missing}")

    return PlannerInput.from_dict(data)

def export_json_and_markdown(
    pi: PlannerInput,
    json_out: str = "exported_data.json",
    md_out: str = "exported_data.md",
) -> None:
    # construct dict
    data_dict = {
        "entity_id": pi.entity_id,
        "goal": pi.Goal.goal,
        "context": {
            "entities": pi.C_set.entities,
            "relations": getattr(pi.C_set, "relations", []),
            "rules": getattr(pi.C_set, "rules", []),
        },
        "candidates": [
            {
                "id": cd.id,
                "trajectory": {
                    "time": cd.traj.time,
                    "states": cd.traj.states,
                },
                "semantics": {
                    "semantic_entity": cd.sem.semantic_entity,
                    "semantic_zones": getattr(cd.sem, "semantic_zones", None),
                    "semantic_score": getattr(cd.sem, "semantic_score", None),
                },
            }
            for cd in pi.Cd_set
        ],
    }

    # Write JSON
    with open(json_out, "w", encoding="utf-8") as f:
        json.dump(data_dict, f, indent=2, ensure_ascii=False)
    print(f"Export completed! Wrote {json_out}")

    # Write Markdown
    md = []
    md.append("# input data\n")
    md.append("## Goal\n")
    md.append(f"{pi.goal.goal}\n")
    md.append("## Entity ID\n")
    md.append(f"{pi.entity_id}\n")
    md.append("## Context: Entities\n")
    md.append(f"{pi.context.entities}\n")
    md.append("## Context: Relations\n")
    md.append(f"{getattr(pi.context, 'relations', [])}\n")
    md.append("## Context: Rules\n")
    md.append(f"{getattr(pi.context, 'rules', [])}\n")

    for i, cd in enumerate(pi.Cd_set, start=1):
        md.append(f"\n### Candidate {i}: {cd.id}\n")
        md.append("#### Trajectory time\n")
        md.append(f"{cd.traj.time}\n")
        md.append("#### Trajectory states\n")
        md.append(f"{cd.traj.states}\n")
        md.append("#### Semantic labels\n")
        md.append(f"{cd.sem.semantic_entity}\n")
        md.append("#### Semantic Coordinates\n")
        md.append(f"{getattr(cd.sem, 'semantic_zones', None)}\n")
        md.append("#### Semantic Score\n")
        md.append(f"{getattr(cd.sem, 'semantic_score', None)}\n")

    with open(md_out, "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    print(f"Export completed! Wrote {md_out}")