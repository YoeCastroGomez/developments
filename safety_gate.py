## Phase 4: SafetyGate. Still under construction.
## TODO: workspace range and max step size checks before a command reaches
## the robot (min/max per joint, max step between consecutive commands).


class SafetyGate:
    def __init__(self, limits_by_arm=None, default_joint_limits=None):
        pass

    def check(self, arm_id: str, joint_id: int, position: int, current_position: int) -> tuple[bool, str]:
        """Returns (allowed, reason). Still under construction: allows everything for now."""
        return True, "ok"
