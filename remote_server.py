import asyncio
import websockets
from fake_robot_hand import RobotFakeHand


class Server_Teleop:
    def __init__(self) :
        self.robot = RobotFakeHand()
      
    def process_robot(self,joint_id : int,position : int ):
        self.robot.move_specific_position(joint_id,position)
       
    async def manejar_conexion(self,websocket):
        async for mensaje in websocket:
            try:
                message_converted = mensaje.split(",")
                joint_id= int (message_converted[0])
                position = int (message_converted[1])
                print(f"I received of client the next instructions: {mensaje}")
                self.process_robot(joint_id,position)
                await websocket.send(f"data : {self.robot.get_state()}")
            except ValueError:
                await websocket.send(f"Usa el formato 'joint_id,position' ") 
            except IndexError:
                await websocket.send(f"El string esta incompleto, no se encuentra datos suficientes")    
        
        

 


async def main():
    print("Servidor escuchando en el puerto 8765...")
    Teleop = Server_Teleop()
    async with websockets.serve(Teleop.manejar_conexion, "localhost", 8765):
        await asyncio.Future()

asyncio.run(main())