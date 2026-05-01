import json

prompt = """You are a semantic safety planner operating in a 2D enclosed room.

Safety is the highest priority and overrides all other objectives.

You will be given an image depicting the environment along with a text prompt.

It contains:
- start position
- goal position
- semantic zones containing a value between 0 - 1 (0 being completely safe and 1 being completely unsafe)
- candidate trajectories

Your task is to:
1) Evaluate each candidate trajectory relative to the zones in context.
2) Generate 3-7 safety rules explaining how safety is evaluated.
3) Assign a rank to each candidate (rank 1 = safest / lowest total risk).
   - If multiple candidates have very similar total risk, they MUST share the same rank (ties allowed).
   - If ties occur, ranks should skip appropriately (e.g., 1, 1, 3).
4) Return ONLY valid JSON in the required PLANNER_OUTPUT_JSON format.

----------------------------------------
SAFETY EVALUATION PROCEDURE (MUST FOLLOW)

A) Identify zones:
   Zones are entities where entity["type"] == "zone".
   Each zone has:
     - bounds (xmin, ymin, xmax, ymax)
     - semantic_score (this represents RISK; higher = more dangerous)

B) A trajectory state (x, y) is inside a zone if:
   xmin <= x <= xmax AND ymin <= y <= ymax

C) Exposure calculation:
   - Count how many trajectory states fall inside each zone.
   - For each zone:
       weighted_zone_risk = zone_risk * count_in_zone
   - Total risk = sum(weighted_zone_risk over all zones)

D) Ranking:
   - Sort candidates by increasing total risk.
   - Lowest total risk => rank 1.
   - Equal total risk => same rank.

E) REQUIRED INTERMEDIATE OUTPUT (MUST COMPUTE INTERNALLY BEFORE RANKING):
    For each candidate, compute and reason step-by-step:

    - count_in_zone for every zone
    - weighted_zone_risk for every zone
    - total_risk

    Candidates with identical total_risk MUST receive identical ranks.
    If two candidates have identical trajectory states, they MUST receive identical total_risk and identical rank.

----------------------------------------
RULE REQUIREMENTS

- Produce 3-7 rules.
- rule_id format: "R1", "R2", ...
- priority: integer (1 = highest)
- scope: "global" unless specific to a zone (e.g. "zone:zone_a")
- Rules must be short, concrete, and consistent with the evaluation procedure.

----------------------------------------"""

def build_prompt(planner_input_dict: dict) -> str:
    template = """
Return ONLY valid JSON in this exact structure:

{
  "Rules": {
    "Rules": [
      {
        "rule_id": "R1",
        "priority": 1,
        "text": "<RULE_TEXT>",
        "scope": "global"
      }
    ]
  },
  "CandidateEvals": {
    "evaluations": [
      {
        "candidate_id": "<CANDIDATE_ID>",
        "zone_exposures": {
          "zone_a": <COUNT>,
          "zone_b": <COUNT>
        },
        "total_risk": <NUMBER>,
        "rank": <POSITIVE_INTEGER>,
        "justification": "<SHORT_JUSTIFICATION>",
        "violations": ["<RULE_ID>"]
      }
    ]
  }
}
"""
    return (
        prompt
        + "PLANNER_INPUT_JSON:\n"
        + json.dumps(planner_input_dict, indent=2)
        + "\n\n"
        + template
    )