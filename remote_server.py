import asyncio
import websockets
from fake_robot_hand import RobotFakeHand
import arbiter  ## new file added ,control the logs
class Server_Teleop:
    def __init__(self) :
        self.arbiter = arbiter.Arbiter()
        self.estop_activated    = False 
        self.operator_connected = False
        self.robot = RobotFakeHand()
      
    def process_robot(self,joint_id : int,position : int ):
        self.robot.move_specific_position(joint_id,position)
       
         
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
                    joint_id= int (message_converted[0])
                    position = int (message_converted[1])
                    print(f"I received of client the next instructions: {message}")
                    ## added Arbiter 
                    source = self.arbiter.decide(self.operator_connected,self.estop_activated)
                    if source ==arbiter.MovementSource.ESTOP:
                        await websocket.send("Movement blocked: ESTOP active. Send RESET to continue.") 
                    elif source == arbiter.MovementSource.TELEOP:
                        self.process_robot(joint_id,position)
                        await websocket.send(f"data : {self.robot.get_state()}")
                    else :
                        await websocket.send(f"it doesn't allow movement.")   
                        
                except ValueError:
                    await websocket.send(f"Use the format 'joint_id,position'. ") 
                except IndexError:
                    await websocket.send(f"String is incompleted,there are insufficient data.")    
        
        self.operator_connected = False
        

 


async def main():
    print("Server listening int port 8765...")
    Teleop = Server_Teleop()
    async with websockets.serve(Teleop.handle_connection, "localhost", 8765):
        await asyncio.Future()

asyncio.run(main())