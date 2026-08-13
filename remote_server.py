import asyncio
import websockets
from fake_robot_hand import RobotFakeHand

def process_robot(joint_id : int,position : int ,robot : RobotFakeHand):
    robot.move_specific_position(joint_id,position)
    

async def manejar_conexion(websocket):
    robot = RobotFakeHand()
    async for mensaje in websocket:
        try:
            message_converted = mensaje.split(",")
            joint_id= int (message_converted[0])
            position = int (message_converted[1])
            print(f"I received of client the next instructions: {mensaje}")
            process_robot(joint_id,position,robot)
            await websocket.send(f"data : {robot.get_state()}")
        except ValueError:
            await websocket.send(f"Usa el formato 'joint_id,position' ") 
        except IndexError:
            await websocket.send(f"El string esta incompleto, no se encuentra datos suficientes")    

async def main():
    print("Servidor escuchando en el puerto 8765...")
    async with websockets.serve(manejar_conexion, "localhost", 8765):
        await asyncio.Future()

asyncio.run(main())