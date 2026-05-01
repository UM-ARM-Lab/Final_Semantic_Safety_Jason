#*********************************************\example input/************************************************

# our goal set :)
# shared_goal = User_Goal(
#     goal=[
#         "deliver surgical instrument safely",
#         "avoid patient and staff", #maybe later it will not need this crutch hopefully 
#         "respect sterility" #similary with this tag
#     ]
# )

# #semantic labels have chords tied to them and then it should rzn that these chords are "unsafe", and should be avoided

# #context set 
# shared_context = Context_set(
#     entities={
#         "patient": {"type": "human", "pos": (0.0, 0.0)},
#         "surgeon": {"type": "human", "pos": (1.0, 0.5)},
#         "sterile_table": {"type": "surface", "pos": (0.5, 1.0)},
#         "waste_bin": {"type": "container", "pos": (-0.5, 1.0)}
#     }
# )

# # trajectory sets 
# traj_1 = Trajectory(
#     t=[0.0, 0.5, 1.0],
#     states=[
#         {"pos": (0.5, 1.0)},
#         {"pos": (0.8, 0.8)},
#         {"pos": (1.0, 0.6)}
#     ],
# )

# traj_2 = Trajectory(
#     t=[0.0, 0.5, 1.0],
#     states=[
#         {"pos": (0.5, 1.0)},
#         {"pos": (0.2, 0.2)},   # passes close to patient
#         {"pos": (1.0, 0.6)}
#     ],
# )

# traj_3 = Trajectory(
#     t=[0.0, 0.5, 1.0],
#     states=[
#         {"pos": (0.5, 1.0)},
#         {"pos": (0.8, 0.8)},
#         {"pos": (0.5, 1.0)}    # returns to sterile table
#     ],
# )

# # semantic labels set
# sem_1 = Semantic_label(
#     semantic_entity={
#         "held_object": {
#             "tags": ["sharp", "metallic"],
#             "parts": {
#                 "handle": ["grasped"],
#                 "blade": ["sharp", "no_touch"]
#             },
#             "state": {"sterility": "sterile"}
#         }
#     }
# )

# sem_2 = Semantic_label(
#     semantic_entity={
#         "held_object": {
#             "tags": ["sharp", "metallic"],
#             "parts": {
#                 "handle": ["grasped"],
#                 "blade": ["sharp", "exposed"]
#             },
#             "state": {"sterility": "sterile"}
#         }
#     }
# )

# sem_3 = Semantic_label(
#     semantic_entity={
#         "held_object": {
#             "tags": ["sharp", "metallic"],
#             "parts": {
#                 "handle": ["grasped"],
#                 "blade": ["sharp"]
#             },
#             "state": {"sterility": "unsterile"}  # key difference
#         }
#     }
# )

# # Candidate trajectories and their paired semantic interpretations
# candidates = [
#     Candidate(traj_1, sem_1, candidate_id="candidate_0"),
#     Candidate(traj_2, sem_2, candidate_id="candidate_1"),
#     Candidate(traj_3, sem_3, candidate_id="candidate_2"),
# ]

# # One planner_input holding everything
# pi = planner_input(
#     Candidate=candidates,
#     Context_set=shared_context,
#     User_Goal=shared_goal,
#     entity_id="robot_eef"   # or "spot_base" / "spot_arm_eef" later
# )

#***************************\example instantiation/*********************************
# env2_input = {
#     "entity_id": "robot_1",
#     "goal": ["move from start to goal safely"],

#     "context": {
#         "entities": {
#             "world": {
#                 "type": "workspace",
#                 "bounds": {"xmin": 0.0, "ymin": 0.0, "xmax": 10.0, "ymax": 10.0}
#             },

#             "zone_bl": {  # bottom-left 4x4
#                 "type": "zone",
#                 "name": "bottom_left_zone",
#                 "bounds": {"xmin": 0.0, "ymin": 0.0, "xmax": 4.0, "ymax": 4.0},
#                 "note": "demo zone for LLM testing",
#                 "semantic_score": 0.25
#             },

#             "zone_tr": {  # top-right 9x9 (anchored at top-right)
#                 "type": "zone",
#                 "name": "top_right_zone",
#                 "bounds": {"xmin": 1.0, "ymin": 1.0, "xmax": 10.0, "ymax": 10.0},
#                 "note": "demo zone for LLM testing",
#                 "semantic_score": 0.80
#             },

#             "start": {"type": "point", "x": 0.5, "y": 0.5},
#             "goal":  {"type": "point", "x": 9.5, "y": 9.5},
#         },

#         "relations": [
#             {"type": "contains", "a": "world", "b": "zone_bl"},
#             {"type": "contains", "a": "world", "b": "zone_tr"},
#         ],

#         "rules": [
#             {"type": "demo_rule", "text": "Prefer trajectories that avoid high-risk zones."}
#         ],
#     },

#     "candidates": [
#         {
#             "id": "traj_1_diagonal",
#             "trajectory": {
#                 "time": [0, 1, 2, 3, 4],
#                 "states": [
#                     {"x": 0.5, "y": 0.5},
#                     {"x": 2.5, "y": 2.5},
#                     {"x": 5.0, "y": 5.0},
#                     {"x": 7.5, "y": 7.5},
#                     {"x": 9.5, "y": 9.5},
#                 ],
#             },
#             "semantics": {
#                 "semantic_entity": {
#                     "candidate_id": "traj_1_diagonal",
#                     "description": "Straight line from start to goal (diagonal)."
#                 },
#                 "semantic_zones": [
#                     # bottom-left zone corners (size 4)
#                     [(0.0, 0.0), (4.0, 0.0), (4.0, 4.0), (0.0, 4.0)],
#                     # top-right zone corners (size 9 anchored at top-right)
#                     [(1.0, 1.0), (10.0, 1.0), (10.0, 10.0), (1.0, 10.0)],
#                 ],
#                 "semantic_score": 0.55,
#             },
#         },

#         {
#             "id": "traj_2_bottom_then_up",
#             "trajectory": {
#                 "time": [0, 1, 2, 3, 4, 5],
#                 "states": [
#                     {"x": 0.5, "y": 0.5},
#                     {"x": 3.5, "y": 0.5},
#                     {"x": 6.5, "y": 0.5},
#                     {"x": 9.5, "y": 0.5},
#                     {"x": 9.5, "y": 5.0},
#                     {"x": 9.5, "y": 9.5},
#                 ],
#             },
#             "semantics": {
#                 "semantic_entity": {
#                     "candidate_id": "traj_2_bottom_then_up",
#                     "description": "Moves along bottom edge, then goes upward near x=9.5."
#                 },
#                 "semantic_zones": [
#                     [(0.0, 0.0), (4.0, 0.0), (4.0, 4.0), (0.0, 4.0)],
#                     [(1.0, 1.0), (10.0, 1.0), (10.0, 10.0), (1.0, 10.0)],
#                 ],
#                 "semantic_score": 0.70,
#             },
#         },

#         {
#             "id": "traj_3_left_then_right",
#             "trajectory": {
#                 "time": [0, 1, 2, 3, 4, 5],
#                 "states": [
#                     {"x": 0.5, "y": 0.5},
#                     {"x": 0.5, "y": 3.5},
#                     {"x": 0.5, "y": 6.5},
#                     {"x": 0.5, "y": 9.5},
#                     {"x": 5.0, "y": 9.5},
#                     {"x": 9.5, "y": 9.5},
#                 ],
#             },
#             "semantics": {
#                 "semantic_entity": {
#                     "candidate_id": "traj_3_left_then_right",
#                     "description": "Moves up along left edge, then goes right along top edge."
#                 },
#                 "semantic_zones": [
#                     [(0.0, 0.0), (4.0, 0.0), (4.0, 4.0), (0.0, 4.0)],
#                     [(1.0, 1.0), (10.0, 1.0), (10.0, 10.0), (1.0, 10.0)],
#                 ],
#                 "semantic_score": 0.35,
#             },
#         },
#     ],
# }


# def make_env2_input() -> dict:
#     return {
#         "entity_id": "robot_1",
#         "goal": ["move from start to goal safely"],
#         "context": {
#             "entities": {
#                 "world": {
#                     "type": "workspace",
#                     "bounds": {"xmin": 0.0, "ymin": 0.0, "xmax": 10.0, "ymax": 10.0}
#                 },
#                 "zone_bl": {
#                     "type": "zone",
#                     "name": "bottom_left_zone",
#                     "bounds": {"xmin": 0.0, "ymin": 0.0, "xmax": 4.0, "ymax": 4.0},
#                     "note": "demo zone for LLM testing",
#                     "semantic_score": 0.25
#                 },
#                 "zone_tr": {
#                     "type": "zone",
#                     "name": "top_right_zone",
#                     "bounds": {"xmin": 1.0, "ymin": 1.0, "xmax": 10.0, "ymax": 10.0},
#                     "note": "demo zone for LLM testing",
#                     "semantic_score": 0.80
#                 },
#                 "start": {"type": "point", "x": 0.5, "y": 0.5},
#                 "goal":  {"type": "point", "x": 9.5, "y": 9.5},
#             },
#             "relations": [
#                 {"type": "contains", "a": "world", "b": "zone_bl"},
#                 {"type": "contains", "a": "world", "b": "zone_tr"},
#             ],
#             "rules": [
#                 {"type": "demo_rule", "text": "Prefer trajectories that avoid high-risk zones."}
#             ],
#         },
#         "candidates": [
#             {
#                 "id": "traj_1_diagonal",
#                 "trajectory": {
#                     "time": [0, 1, 2, 3, 4],
#                     "states": [
#                         {"x": 0.5, "y": 0.5},
#                         {"x": 2.5, "y": 2.5},
#                         {"x": 5.0, "y": 5.0},
#                         {"x": 7.5, "y": 7.5},
#                         {"x": 9.5, "y": 9.5},
#                     ],
#                 },
#                 "semantics": {
#                     "semantic_entity": {"candidate_id": "traj_1_diagonal", "description": "Diagonal"},
#                     "semantic_zones": [
#                         [(0.0, 0.0), (4.0, 0.0), (4.0, 4.0), (0.0, 4.0)],
#                         [(1.0, 1.0), (10.0, 1.0), (10.0, 10.0), (1.0, 10.0)],
#                     ],
#                     "semantic_score": 0.55,
#                 },
#             },
#             {
#                 "id": "traj_2_bottom_then_up",
#                 "trajectory": {
#                     "time": [0, 1, 2, 3, 4, 5],
#                     "states": [
#                         {"x": 0.5, "y": 0.5},
#                         {"x": 3.5, "y": 0.5},
#                         {"x": 6.5, "y": 0.5},
#                         {"x": 9.5, "y": 0.5},
#                         {"x": 9.5, "y": 5.0},
#                         {"x": 9.5, "y": 9.5},
#                     ],
#                 },
#                 "semantics": {
#                     "semantic_entity": {"candidate_id": "traj_2_bottom_then_up", "description": "Bottom then up"},
#                     "semantic_zones": [
#                         [(0.0, 0.0), (4.0, 0.0), (4.0, 4.0), (0.0, 4.0)],
#                         [(1.0, 1.0), (10.0, 1.0), (10.0, 10.0), (1.0, 10.0)],
#                     ],
#                     "semantic_score": 0.70,
#                 },
#             },
#             {
#                 "id": "traj_3_left_then_right",
#                 "trajectory": {
#                     "time": [0, 1, 2, 3, 4, 5],
#                     "states": [
#                         {"x": 0.5, "y": 0.5},
#                         {"x": 0.5, "y": 3.5},
#                         {"x": 0.5, "y": 6.5},
#                         {"x": 0.5, "y": 9.5},
#                         {"x": 5.0, "y": 9.5},
#                         {"x": 9.5, "y": 9.5},
#                     ],
#                 },
#                 "semantics": {
#                     "semantic_entity": {"candidate_id": "traj_3_left_then_right", "description": "Left then right"},
#                     "semantic_zones": [
#                         [(0.0, 0.0), (4.0, 0.0), (4.0, 4.0), (0.0, 4.0)],
#                         [(1.0, 1.0), (10.0, 1.0), (10.0, 10.0), (1.0, 10.0)],
#                     ],
#                     "semantic_score": 0.35,
#                 },
#             },
#         ],
#     }

# from environments import planner_input

# prompt = """
# You are a semantic safety planner operating in a 2D enclosed room.

# The room has:

# Fixed spatial bounds

# One or more semantic zones that may represent risk or danger

# Multiple candidate trajectories that move from the bottom side of the room to the top side of the room

# Safety is the highest priority and overrides all other objectives.

# Task

# Given the provided room context and candidate trajectories:

# Evaluate each candidate trajectory based on how safe it is.

# Assign a semantic safety score to each trajectory on a scale from 0 to 10:

# 10 = extremely safe (minimal or no exposure to risk)

# 0 = extremely dangerous (significant exposure to high-risk zones)

# Choose exactly one trajectory that is the safest overall.

# Evaluation Guidelines (in priority order)

# Minimize time spent inside high-risk semantic zones

# Prefer trajectories that avoid dangerous zones entirely

# If all trajectories intersect risk zones, choose the one with the least exposure

# The trajectory must successfully move from the bottom side to the top side of the room

# Instructions

# Analyze each trajectory internally before answering.

# Do not assume all trajectories are equally safe.

# Be objective and consistent in scoring.

# Do not include step-by-step reasoning outside the required fields.

# Required Output Format

# Return only valid JSON in the following format:

# {
#   "chosen_candidate_id": "<candidate_id>",
#   "path_safety_scores": {
#     "<candidate_id>": {
#       "safety_score": 0,
#       "justification": "brief explanation"
#     }
#   },
#   "final_explanation": "concise explanation of why the chosen path is the safest overall"
# }

# Hard Constraints

# Choose exactly one trajectory.

# Provide a safety score and justification for every candidate trajectory.

# Do not include any text outside the JSON.

# Do not include chain-of-thought or hidden reasoning.

# """

    # prompt = f"""
    # You are a robot navigating from Start to Goal.

    # The candidate trajectories are:
    # {traj_ids}

    # Rank ALL trajectories from best to worst.

    # IMPORTANT:
    # - Include every trajectory exactly once
    # - Do not omit any

    # Return valid JSON only in this format:
    # {{
    # "ranking": [
    #     {{"rank": 1, "trajectory": "traj_x"}} #"reason": "..."
    # ]
    # }}
    # """