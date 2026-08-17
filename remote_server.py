## Phase 2: client-server control channel (WebSocket server).
## Also wires in Phase 3 (Arbiter) and Phase 4 (SafetyGate).

import asyncio
import websockets
from robot_py_bullet_sim import RobotPyBullet
import arbiter  ## new file added ,control the logs
import safety_gate  ## Phase 4: range/speed clamp before moving the robot

ARM_IDS = ("left", "right")  ## a robot has two arms -> two RobotPyBullet instances
ARM_BASE_POSITIONS = {"left": (0, 0, 0), "right": (1, 0, 0)}  ## side by side, no overlap

class Server_Teleop:
    def __init__(self) :
        self.arbiter = arbiter.Arbiter()
        self.safety_gate = safety_gate.SafetyGate()
        self.estop_activated    = False
        self.operator_connected = False
        ## one robot, two arms: an independent RobotPyBullet instance per arm,
        ## sharing the same PyBullet physics world (see _ensure_connected)
        self.robots = {arm_id: RobotPyBullet(arm_id, base_position=ARM_BASE_POSITIONS[arm_id]) for arm_id in ARM_IDS}

    def process_robot(self,arm_id : str,joint_id : int,position : int ):
        self.robots[arm_id].move_specific_position(joint_id,position)


    def reset_estop(self):
        """Desactivate the e-stop. Always may be an explicit human action."""
        self.estop_activated = False
        print("ESTOP desactivated")
        
    def check_hardware_estop_conditions(self, message) -> bool:
        if self.estop_activated:
            return True
        if message == "ESTOP":
            return True
        return False         
        
    async def handle_connection(self,websocket):
        self.operator_connected= True
        async for message in websocket:
            if message == "RESET":
                self.reset_estop()
                await websocket.send("ESTOP desactivated")
            elif message == "ESTOP":
                self.estop_activated = self.check_hardware_estop_conditions(message)
                await websocket.send("ESTOP activated")
            else:

                try:
                    message_converted = message.split(",")
                    arm_id = message_converted[0].strip()
                    joint_id= int (message_converted[1])
                    position = int (message_converted[2])
                    print(f"I received of client the next instructions: {message}")
                    if arm_id not in self.robots:
                        await websocket.send(f"Unknown arm_id '{arm_id}'. Use one of {ARM_IDS}.")
                        continue
                    ## added Arbiter
                    source = self.arbiter.decide(self.operator_connected,self.estop_activated)
                    if source ==arbiter.MovementSource.ESTOP:
                        await websocket.send("Movement blocked: ESTOP active. Send RESET to continue.")
                    elif source == arbiter.MovementSource.TELEOP:
                        current_position = self.robots[arm_id].get_state()[joint_id]
                        allowed, reason = self.safety_gate.check(arm_id, joint_id, position, current_position)
                        if not allowed:
                            await websocket.send(f"Movement blocked by SafetyGate: {reason}.")
                        else:
                            self.process_robot(arm_id,joint_id,position)
                            await websocket.send(f"data : {arm_id} -> {self.robots[arm_id].get_state()}")
                    else :
                        await websocket.send(f"it doesn't allow movement.")

                except ValueError:
                    await websocket.send(f"Use the format 'arm_id,joint_id,position' (arm_id in {ARM_IDS}). ")
                except IndexError:
                    await websocket.send(f"String is incompleted,there are insufficient data.")
        
        self.operator_connected = False
        

 


async def main():
    print("Server listening int port 8765...")
    Teleop = Server_Teleop()
    async with websockets.serve(Teleop.handle_connection, "localhost", 8765):
        await asyncio.Future()

asyncio.run(main())