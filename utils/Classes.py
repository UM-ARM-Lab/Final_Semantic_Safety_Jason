
class UserGoal:
    def __init__(self, goal: list[str]):
        self.goal = goal

    @classmethod
    def from_dict(cls, d: dict):
        return cls(goal=list(d["goal"]))


class ContextSet:
    def __init__(self, entities: dict, relations=None, rules=None):
        self.entities = entities
        self.relations = [] if relations is None else list(relations)
        self.rules = [] if rules is None else list(rules)


    @classmethod
    def from_dict(cls, d: dict):
        return cls(
            entities=dict(d["entities"]),
            relations=list(d.get("relations", [])),
            rules=list(d.get("rules", [])),
        )


class SemanticLabel:
    def __init__(
        self,
        semantic_entity: dict,
        semantic_zone_id: str,
        semantic_description: str,
        semantic_zones: list | None = None,

    ):
        self.semantic_entity = dict(semantic_entity)
        self.semantic_zone_id = semantic_zone_id
        self.semantic_description = semantic_description

        if semantic_zones is None:
            self.semantic_zones = None

    @classmethod
    def from_dict(cls, d: dict):
        if not isinstance(d, dict):
            raise ValueError("Input to SemanticLabel.from_dict must be a dictionary")

        semantic_entity = d.get("semantic_entity")
        semantic_zone_id = d.get("semantic_zone_id")
        semantic_description = d.get("semantic_description")
        semantic_zones = d.get("semantic_zones", None)

        return cls(
            semantic_entity=semantic_entity,
            semantic_zone_id=semantic_zone_id,
            semantic_description=semantic_description,
            semantic_zones=semantic_zones,
        )

    def to_dict(self) -> dict:
        return {
            "semantic_entity": self.semantic_entity,
            "semantic_zone_id": self.semantic_zone_id,
            "semantic_description": self.semantic_description,
            "semantic_zones": self.semantic_zones,
        }


class Trajectory:
    def __init__(self, time: list[float], states: list[dict]):
        self.time = time
        self.states = states
    
    @classmethod
    def from_dict(cls, d: dict):
        if "time" not in d:
            raise KeyError(f"Trajectory missing 'time'. Keys found: {list(d.keys())}. Full traj dict: {d}")
        if "states" not in d:
            raise KeyError(f"Trajectory missing 'states'. Keys found: {list(d.keys())}. Full traj dict: {d}")
        return cls(time=list(d["time"]), states=list(d["states"]))



class Candidate:
    def __init__(
        self,
        trajectory: Trajectory,
        semantics: list[SemanticLabel] | None = None,
        candidate_id: str | None = None,
    ):
        self.id = candidate_id
        self.traj = trajectory
        self.sem = [] if semantics is None else list(semantics)

    @classmethod
    def from_dict(cls, d: dict):
        if "trajectory" not in d:
            raise ValueError("Candidate must contain a 'trajectory' field")

        # Parse trajectory
        trajectory = Trajectory.from_dict(d["trajectory"])

        # Parse semantic labels (LIST!)
        semantics_data = d.get("semantics", [])
        if not isinstance(semantics_data, list):
            raise ValueError("'semantics' must be a list")

        semantics = [SemanticLabel.from_dict(s) for s in semantics_data]

        return cls(
            trajectory=trajectory,
            semantics=semantics,
            candidate_id=d.get("id"),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "trajectory": self.traj.to_dict(),
            "semantics": [s.to_dict() for s in self.sem],
        }


class PlannerInput:
    def __init__(self, candidates: list[Candidate], context: ContextSet, goal: UserGoal, entity_id: str):
        self.candidates = candidates
        self.context = context
        self.goal = goal
        self.entity_id = entity_id

    @classmethod
    def from_dict(cls, d: dict):
        return cls(
            candidates=[Candidate.from_dict(c) for c in d["candidates"]],
            context=ContextSet.from_dict(d["context"]),
            goal=UserGoal.from_dict(d),
            entity_id=d["entity_id"],
        )
    
class Rule:
    def __init__(self, rule_id: str, priority: int, text: str, scope: str):
        self.rule_id = rule_id
        self.priority = priority
        self.text = text
        self.scope = scope

class RuleSet:
    def __init__(self, Rules: list[Rule]):
        self.Rules = Rules

class CandidateEvaluation:
    def __init__(
        self,
        candidate_id: str,
        safety_score: float,
        justification: str,
        violations: list[str] | None = None,
        zone_exposures: dict | None = None,
        entity_clearances: dict | None = None,
    ):
        self.candidate_id = candidate_id
        self.safety_score = float(safety_score)
        self.justification = justification
        self.violations = [] if violations is None else list(violations)


class EvaluationSet:
    def __init__(self, evaluations: list[CandidateEvaluation]):
        self.evaluations = evaluations

class PlannerOutput:
    def __init__(self, Rules: RuleSet, CandidateEvals: EvaluationSet):
        self.Rules = Rules
        self.CandidateEvals = CandidateEvals

#git@github.com:UM-ARM-Lab/SemanticSafety-Jason.git