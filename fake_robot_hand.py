class RobotFakeHand:
    def __init__(self):
        self.joint_positions =[0,0,0,0,0]
    def move_specific_position(self,joint_id,position):
        print(f"[Simulated] joint {joint_id} -> {position}")
        self.joint_positions[joint_id]=position
        
    def get_state(self):
        return self.joint_positions
    
    
    
robot = RobotFakeHand()
robot.move_specific_position(2,45)
print(robot.get_state())  