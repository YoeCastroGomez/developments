## Phase 1: local control interface (hardware mock).

class RobotFakeHand:
    """Represents a single robotic hand/arm. A robot with two arms is modeled
    as two independent instances of this class. Original Phase 1 mock; kept
    for reference, remote_server.py now uses RobotPyBullet instead."""
    def __init__(self,name="hand"):
        self.name = name
        self.joint_positions =[0,0,0,0,0]
    def move_specific_position(self,joint_id,position):
        print(f"[Simulated] arm '{self.name}' joint {joint_id} -> {position}")
        self.joint_positions[joint_id]=position

    def get_state(self):
        return self.joint_positions
    
    
    
robot = RobotFakeHand("left")
robot.move_specific_position(2,45)
print(robot.get_state())