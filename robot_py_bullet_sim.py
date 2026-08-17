## Not part of a numbered phase yet: PyBullet physics prototype.
## Used by remote_server.py as the robot behind each arm.

import pybullet as p
import pybullet_data
import math
import time

_physics_client = None  ## one shared physics world for all arms


def _ensure_connected():
    """Connects to PyBullet once, no matter how many arms get instantiated."""
    global _physics_client
    if _physics_client is None:
        _physics_client = p.connect(p.GUI)
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0, 0, -9.8)
        p.loadURDF("plane.urdf")
    return _physics_client


class RobotPyBullet:
    """PyBullet simulation of a single robotic arm (Kuka IIWA).

    Same interface as RobotFakeHand (move_specific_position, get_state) so it
    can be swapped in without touching the rest of the system. A two-armed
    robot is built by instantiating this twice, each with its own
    base_position, inside the same shared physics world (same pattern as
    fake_robot_hand.py)."""

    STEPS_PER_MOVE = 60  ## simulation steps run so the arm actually reaches the target

    def __init__(self, name="hand", base_position=(0, 0, 0)):
        _ensure_connected()
        self.name = name
        self.robot_id = p.loadURDF("kuka_iiwa/model.urdf", basePosition=list(base_position))
        self.num_joints = p.getNumJoints(self.robot_id)
        self.joint_positions = [0] * self.num_joints

    def move_specific_position(self, joint_id, position):
        if not (0 <= joint_id < self.num_joints):
            raise IndexError(f"joint_id {joint_id} out of range for arm '{self.name}' (0..{self.num_joints - 1})")

        rad = position * (math.pi / 180)
        p.setJointMotorControl2(self.robot_id, joint_id, p.POSITION_CONTROL, targetPosition=rad)

        ## step the simulation so the arm actually reaches the target,
        ## not just tell the motor where to go
        for _ in range(self.STEPS_PER_MOVE):
            p.stepSimulation()
            time.sleep(1 / 240)

        self.joint_positions[joint_id] = position
        print(f"[PyBullet] arm '{self.name}' joint {joint_id} -> {position} deg")

    def get_state(self):
        return self.joint_positions


if __name__ == "__main__":
    ## manual test: two arms side by side
    left_arm = RobotPyBullet("left", base_position=(0, 0, 0))
    right_arm = RobotPyBullet("right", base_position=(1, 0, 0))

    left_arm.move_specific_position(3, 45)
    right_arm.move_specific_position(2, 30)

    print("left:", left_arm.get_state())
    print("right:", right_arm.get_state())

    while True:
        p.stepSimulation()
        time.sleep(1 / 240)
