## Not part of a numbered phase yet: loose PyBullet test script, the
## non-object-oriented version of robot_py_bullet_sim.py.

import pybullet as p
import pybullet_data
import time
import math

p.connect(p.GUI)
p.setAdditionalSearchPath(pybullet_data.getDataPath())
p.setGravity(0, 0, -9.8)
p.loadURDF("plane.urdf")

robot = p.loadURDF("kuka_iiwa/model.urdf", basePosition=[0, 0, 0])
num_joints = p.getNumJoints(robot)
grades = 45
rad = grades*(math.pi/180)
p.setJointMotorControl2(robot,3,p.POSITION_CONTROL,targetPosition =rad)
while True:
    p.stepSimulation()
    time.sleep(1/240)