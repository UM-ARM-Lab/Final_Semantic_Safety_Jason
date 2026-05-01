# easy map:
planner_input = {
    "entity_id": "robot_1",
    "goal": ["move from start to goal safely"],
    "context": {
        "entities": {
            "world": {
                "type": "workspace",
                "bounds": {"xmin": 0.0, "ymin": 0.0, "xmax": 1.0, "ymax": 1.0},
            },

            # Top-left: wet region
            "wet area": {
                "type": "zone",
                "name": "slippery Area",
                "bounds": {"xmin": 0.15, "ymin": 0.64, "xmax": 0.33, "ymax": 0.82},
                "semantic_entity": {
                    "type": "surface_condition",
                    "description": "Wet surface with reduced traction."
                },
            },

            # Bottom-right rectangle 1: icy
            "very icy": {
                "type": "zone",
                "name": "Icy Area 1",
                "bounds": {"xmin": 0.52, "ymin": 0.08, "xmax": 0.73, "ymax": 0.26},
                "semantic_entity": {
                    "type": "surface_condition",
                    "description": "Extremely slippery icy surface."
                },
            },

            # Bottom-right rectangle 2: icy
            "icy": {
                "type": "zone",
                "name": "Icy Area 2",
                "bounds": {"xmin": 0.70, "ymin": 0.14, "xmax": 0.88, "ymax": 0.44},
                "semantic_entity": {
                    "type": "surface_condition",
                    "description": "Extremely slippery icy surface."
                },
            },

            "start": {"type": "point", "x": 0.08, "y": 0.08},
            "goal": {"type": "point", "x": 0.92, "y": 0.92},
        },

        "relations": [
            {"type": "contains", "a": "world", "b": "zone_wet"},
            {"type": "contains", "a": "world", "b": "zone_icy_1"},
            {"type": "contains", "a": "world", "b": "zone_icy_2"},
        ],
    },

    "candidates": [

        # Upper path: goes high and skims / nears wet zone
        {
            "id": "traj_1",
            "trajectory": {
                "time": [0, 1, 2, 3, 4, 5],
                "states": [
                    {"x": 0.08, "y": 0.08},
                    {"x": 0.08, "y": 0.55},
                    {"x": 0.14, "y": 0.72},
                    {"x": 0.36, "y": 0.84},
                    {"x": 0.65, "y": 0.90},
                    {"x": 0.92, "y": 0.92},
                ],
            },
            "semantics": [
                {
                    "semantic_entity": {"type": "surface_condition", "label": "slippery_area"},
                    "semantic_zone_id": "zone_wet",
                    "semantic_description": "Trajectory travels near and may skim the wet region.",
                    "semantic_zones": [
                        [0.15, 0.64],
                        [0.33, 0.64],
                        [0.33, 0.82],
                        [0.15, 0.82],
                    ],
                }
            ],
        },

        # Middle path: avoids all zones
        {
            "id": "traj_2",
            "trajectory": {
                "time": [0, 1, 2, 3, 4],
                "states": [
                    {"x": 0.08, "y": 0.08},
                    {"x": 0.25, "y": 0.22},
                    {"x": 0.48, "y": 0.46},
                    {"x": 0.68, "y": 0.68},
                    {"x": 0.92, "y": 0.92},
                ],
            },
            "semantics": [],
        },

        # Bottom path: explicitly goes through icy zones
        {
            "id": "traj_3",
            "trajectory": {
                "time": [0, 1, 2, 3, 4, 5, 6],
                "states": [
                    {"x": 0.08, "y": 0.08},
                    {"x": 0.30, "y": 0.08},
                    {"x": 0.55, "y": 0.12},
                    {"x": 0.68, "y": 0.18},
                    {"x": 0.78, "y": 0.24},
                    {"x": 0.88, "y": 0.50},
                    {"x": 0.92, "y": 0.92},
                ],
            },
            "semantics": [
                {
                    "semantic_entity": {"type": "surface_condition", "label": "very_icy"},
                    "semantic_zone_id": "zone_icy_1",
                    "semantic_description": "Trajectory passes through icy region 1.",
                    "semantic_zones": [
                        [0.52, 0.08],
                        [0.73, 0.08],
                        [0.73, 0.26],
                        [0.52, 0.26],
                    ],
                },
                {
                    "semantic_entity": {"type": "surface_condition", "label": "very_icy"},
                    "semantic_zone_id": "zone_icy_2",
                    "semantic_description": "Trajectory passes through icy region 2.",
                    "semantic_zones": [
                        [0.70, 0.14],
                        [0.88, 0.14],
                        [0.88, 0.44],
                        [0.70, 0.44],
                    ],
                }
            ],
        },
    ],
}

# wrap around 
planner_input = {

    "entity_id": "robot_1",
    "goal": ["move from start to goal safely"],
    "context": {
        "entities": {
            "world": {
                "type": "workspace",
                "bounds": {"xmin": 0.0, "ymin": 0.0, "xmax": 1.0, "ymax": 1.0},
            },

            # Top-left: wet region
            "wet area": {
                "type": "zone",
                "name": "slippery Area",
                "bounds": {"xmin": 0.15, "ymin": 0.64, "xmax": 0.33, "ymax": 0.82},
                "semantic_entity": {
                    "type": "surface_condition",
                    "description": "Wet surface with reduced traction."
                },
            },

            # Bottom-right rectangle 1: icy
            "very icy": {
                "type": "zone",
                "name": "Icy Area 1",
                "bounds": {"xmin": 0.52, "ymin": 0.08, "xmax": 0.73, "ymax": 0.26},
                "semantic_entity": {
                    "type": "surface_condition",
                    "description": "Extremely slippery icy surface."
                },
            },

            # Bottom-right rectangle 2: icy
            "icy": {
                "type": "zone",
                "name": "Icy Area 2",
                "bounds": {"xmin": 0.70, "ymin": 0.14, "xmax": 0.88, "ymax": 0.44},
                "semantic_entity": {
                    "type": "surface_condition",
                    "description": "Extremely slippery icy surface."
                },
            },

            "start": {"type": "point", "x": 0.08, "y": 0.08},
            "goal": {"type": "point", "x": 0.92, "y": 0.92},
        },

        "relations": [
            {"type": "contains", "a": "world", "b": "wet area"},
            {"type": "contains", "a": "world", "b": "very icy"},
            {"type": "contains", "a": "world", "b": "icy"},
        ],
    },

    "candidates": [

        # Upper path: goes high and skims / nears wet zone
        {
            "id": "traj_1",
            "trajectory": {
                "time": [0, 1, 2, 3, 4, 5],
                "states": [
                    {"x": 0.08, "y": 0.08},
                    {"x": 0.08, "y": 0.55},
                    {"x": 0.14, "y": 0.72},
                    {"x": 0.36, "y": 0.84},
                    {"x": 0.65, "y": 0.90},
                    {"x": 0.92, "y": 0.92},
                ],
            },
            "semantics": [
                {
                    "semantic_entity": {"type": "surface_condition", "label": "slippery_area"},
                    "semantic_zone_id": "wet area",
                    "semantic_description": "Trajectory travels near and may skim the wet region.",
                    "semantic_zones": [
                        [0.15, 0.64],
                        [0.33, 0.64],
                        [0.33, 0.82],
                        [0.15, 0.82],
                    ],
                }
            ],
        },

        # Middle path: avoids all zones
        {
            "id": "traj_2",
            "trajectory": {
                "time": [0, 1, 2, 3, 4],
                "states": [
                    {"x": 0.08, "y": 0.08},
                    {"x": 0.25, "y": 0.22},
                    {"x": 0.48, "y": 0.46},
                    {"x": 0.68, "y": 0.68},
                    {"x": 0.92, "y": 0.92},
                ],
            },
            "semantics": [],
        },

        # Bottom path: explicitly goes through icy zones
        {
            "id": "traj_3",
            "trajectory": {
                "time": [0, 1, 2, 3, 4, 5, 6],
                "states": [
                    {"x": 0.08, "y": 0.08},
                    {"x": 0.30, "y": 0.08},
                    {"x": 0.55, "y": 0.12},
                    {"x": 0.68, "y": 0.18},
                    {"x": 0.78, "y": 0.24},
                    {"x": 0.88, "y": 0.50},
                    {"x": 0.92, "y": 0.92},
                ],
            },
            "semantics": [
                {
                    "semantic_entity": {"type": "surface_condition", "label": "very_icy"},
                    "semantic_zone_id": "very icy",
                    "semantic_description": "Trajectory passes through icy region 1.",
                    "semantic_zones": [
                        [0.52, 0.08],
                        [0.73, 0.08],
                        [0.73, 0.26],
                        [0.52, 0.26],
                    ],
                },
                {
                    "semantic_entity": {"type": "surface_condition", "label": "very_icy"},
                    "semantic_zone_id": "icy",
                    "semantic_description": "Trajectory passes through icy region 2.",
                    "semantic_zones": [
                        [0.70, 0.14],
                        [0.88, 0.14],
                        [0.88, 0.44],
                        [0.70, 0.44],
                    ],
                }
            ],
        },

        # Long wraparound path: avoids all semantic zones, but longer than traj_2
        {
            "id": "traj_4",
            "trajectory": {
                "time": [0, 1, 2, 3, 4, 5, 6, 7],
                "states": [
                    {"x": 0.08, "y": 0.08},
                    {"x": 0.04, "y": 0.30},
                    {"x": 0.04, "y": 0.55},
                    {"x": 0.04, "y": 0.80},
                    {"x": 0.04, "y": 0.92},
                    {"x": 0.35, "y": 0.95},
                    {"x": 0.65, "y": 0.95},
                    {"x": 0.92, "y": 0.92},
                ],
            },
            "semantics": [],
        }
    ],
}

# 5 traj 5 zone mess
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

# big car crash
planner_input = {
    "entity_id": "robot_1",
    "goal": ["move from start to goal safely"],
    "context": {
        "entities": {
            "world": {
                "type": "workspace",
                "bounds": {"xmin": 0.0, "ymin": 0.0, "xmax": 1.0, "ymax": 1.0},
            },

            # Large central hazard
            "car crash": {
                "type": "zone",
                "name": "Car Crash",
                "bounds": {"xmin": 0.28, "ymin": 0.28, "xmax": 0.72, "ymax": 0.68},
                "semantic_entity": {
                    "type": "hazard",
                    "description": "A major car crash with debris and blocked passage."
                },
            },

            # Upper-left hazard
            "wet area": {
                "type": "zone",
                "name": "Wet Area",
                "bounds": {"xmin": 0.08, "ymin": 0.68, "xmax": 0.28, "ymax": 0.88},
                "semantic_entity": {
                    "type": "surface_condition",
                    "description": "Wet surface with reduced traction."
                },
            },

            # Lower-right hazard
            "construction site": {
                "type": "zone",
                "name": "Construction Site",
                "bounds": {"xmin": 0.72, "ymin": 0.08, "xmax": 0.92, "ymax": 0.30},
                "semantic_entity": {
                    "type": "hazard",
                    "description": "Active construction area with equipment and obstacles."
                },
            },

            "start": {"type": "point", "x": 0.06, "y": 0.08},
            "goal": {"type": "point", "x": 0.94, "y": 0.92},
        },

        "relations": [
            {"type": "contains", "a": "world", "b": "car crash"},
            {"type": "contains", "a": "world", "b": "wet area"},
            {"type": "contains", "a": "world", "b": "construction site"},
        ],
    },

    "candidates": [
        # traj_1: direct middle path through the crash
        {
            "id": "traj_1",
            "trajectory": {
                "time": [0, 1, 2, 3, 4],
                "states": [
                    {"x": 0.06, "y": 0.08},
                    {"x": 0.24, "y": 0.24},
                    {"x": 0.50, "y": 0.46},
                    {"x": 0.74, "y": 0.70},
                    {"x": 0.94, "y": 0.92},
                ],
            },
            "semantics": [
                {
                    "semantic_entity": {"type": "hazard", "label": "car_crash"},
                    "semantic_zone_id": "car crash",
                    "semantic_description": "Trajectory goes through the car crash zone.",
                    "semantic_zones": [
                        [0.28, 0.28],
                        [0.72, 0.28],
                        [0.72, 0.68],
                        [0.28, 0.68],
                    ],
                }
            ],
        },

        # traj_2: upper wraparound, skims / enters wet area
        {
            "id": "traj_2",
            "trajectory": {
                "time": [0, 1, 2, 3, 4, 5],
                "states": [
                    {"x": 0.06, "y": 0.08},
                    {"x": 0.06, "y": 0.40},
                    {"x": 0.08, "y": 0.72},
                    {"x": 0.24, "y": 0.82},
                    {"x": 0.60, "y": 0.92},
                    {"x": 0.94, "y": 0.92},
                ],
            },
            "semantics": [
                {
                    "semantic_entity": {"type": "surface_condition", "label": "wet_area"},
                    "semantic_zone_id": "wet area",
                    "semantic_description": "Trajectory passes through or skims the wet area.",
                    "semantic_zones": [
                        [0.08, 0.68],
                        [0.28, 0.68],
                        [0.28, 0.88],
                        [0.08, 0.88],
                    ],
                }
            ],
        },

        # traj_3: lower route, passes through construction site
        {
            "id": "traj_3",
            "trajectory": {
                "time": [0, 1, 2, 3, 4, 5, 6],
                "states": [
                    {"x": 0.06, "y": 0.08},
                    {"x": 0.22, "y": 0.08},
                    {"x": 0.42, "y": 0.10},
                    {"x": 0.64, "y": 0.12},
                    {"x": 0.78, "y": 0.18},
                    {"x": 0.90, "y": 0.40},
                    {"x": 0.94, "y": 0.92},
                ],
            },
            "semantics": [
                {
                    "semantic_entity": {"type": "hazard", "label": "construction_site"},
                    "semantic_zone_id": "construction site",
                    "semantic_description": "Trajectory passes through the construction site.",
                    "semantic_zones": [
                        [0.72, 0.08],
                        [0.92, 0.08],
                        [0.92, 0.30],
                        [0.72, 0.30],
                    ],
                }
            ],
        },

        # traj_4: long safe outer-left/top route, avoids all zones
        {
            "id": "traj_4",
            "trajectory": {
                "time": [0, 1, 2, 3, 4, 5, 6, 7],
                "states": [
                    {"x": 0.06, "y": 0.08},
                    {"x": 0.06, "y": 0.25},
                    {"x": 0.06, "y": 0.50},
                    {"x": 0.06, "y": 0.64},
                    {"x": 0.06, "y": 0.92},
                    {"x": 0.35, "y": 0.96},
                    {"x": 0.68, "y": 0.96},
                    {"x": 0.94, "y": 0.92},
                ],
            },
            "semantics": [],
        },

        # traj_5: right-side compromise, avoids crash, avoids wet, but near construction
        {
            "id": "traj_5",
            "trajectory": {
                "time": [0, 1, 2, 3, 4, 5],
                "states": [
                    {"x": 0.06, "y": 0.08},
                    {"x": 0.18, "y": 0.20},
                    {"x": 0.26, "y": 0.72},
                    {"x": 0.76, "y": 0.72},
                    {"x": 0.90, "y": 0.82},
                    {"x": 0.94, "y": 0.92},
                ],
            },
            "semantics": [],
        },
    ],
}

# simple 3 compariosn
planner_input = {
    "entity_id": "robot_1",
    "goal": ["move from start to goal safely"],
    "context": {
        "entities": {
            "world": {
                "type": "workspace",
                "bounds": {"xmin": 0.0, "ymin": 0.0, "xmax": 1.0, "ymax": 1.0},
            },

            "car crash": {
                "type": "zone",
                "name": "Car Crash",
                "bounds": {"xmin": 0.40, "ymin": 0.45, "xmax": 0.55, "ymax": 0.60},
                "semantic_entity": {
                    "type": "hazard",
                    "description": "A small car crash area with debris."
                },
            },

            "wet area": {
                "type": "zone",
                "name": "Wet Area",
                "bounds": {"xmin": 0.18, "ymin": 0.68, "xmax": 0.33, "ymax": 0.83},
                "semantic_entity": {
                    "type": "surface_condition",
                    "description": "A slippery wet area."
                },
            },

            "start": {"type": "point", "x": 0.08, "y": 0.08},
            "goal": {"type": "point", "x": 0.92, "y": 0.92},
        },

        "relations": [
            {"type": "contains", "a": "world", "b": "car crash"},
            {"type": "contains", "a": "world", "b": "wet area"},
        ],
    },

    "candidates": [
        # Goes through the car crash
        {
            "id": "traj_1",
            "trajectory": {
                "time": [0, 1, 2, 3, 4],
                "states": [
                    {"x": 0.08, "y": 0.08},
                    {"x": 0.25, "y": 0.22},
                    {"x": 0.48, "y": 0.52},
                    {"x": 0.70, "y": 0.72},
                    {"x": 0.92, "y": 0.92},
                ],
            },
            "semantics": [
                {
                    "semantic_entity": {"type": "hazard", "label": "car_crash"},
                    "semantic_zone_id": "car crash",
                    "semantic_description": "Trajectory passes through the car crash area.",
                    "semantic_zones": [
                        [0.40, 0.45],
                        [0.55, 0.45],
                        [0.55, 0.60],
                        [0.40, 0.60],
                    ],
                }
            ],
        },

        # Goes through the wet area
        {
            "id": "traj_2",
            "trajectory": {
                "time": [0, 1, 2, 3, 4, 5],
                "states": [
                    {"x": 0.08, "y": 0.08},
                    {"x": 0.08, "y": 0.40},
                    {"x": 0.18, "y": 0.72},
                    {"x": 0.32, "y": 0.80},
                    {"x": 0.60, "y": 0.88},
                    {"x": 0.92, "y": 0.92},
                ],
            },
            "semantics": [
                {
                    "semantic_entity": {"type": "surface_condition", "label": "wet_area"},
                    "semantic_zone_id": "wet area",
                    "semantic_description": "Trajectory passes through the wet area.",
                    "semantic_zones": [
                        [0.18, 0.68],
                        [0.33, 0.68],
                        [0.33, 0.83],
                        [0.18, 0.83],
                    ],
                }
            ],
        },

        # Avoids both zones
        {
            "id": "traj_3",
            "trajectory": {
                "time": [0, 1, 2, 3, 4, 5],
                "states": [
                    {"x": 0.08, "y": 0.08},
                    {"x": 0.25, "y": 0.12},
                    {"x": 0.50, "y": 0.20},
                    {"x": 0.72, "y": 0.45},
                    {"x": 0.84, "y": 0.70},
                    {"x": 0.92, "y": 0.92},
                ],
            },
            "semantics": [],
        },
    ],
}


