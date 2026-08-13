import asyncio
import websockets
import time 

async def conectar():
    async with websockets.connect("ws://localhost:8765") as websocket:
        while(True):
          text = input("Write coordenates like '[joint_id,position]'")
          if(text=="0"): break 
          start_time = time.time() 
          await websocket.send(text)
          respuesta = await websocket.recv()
          end_time = time.time()
          print(f"El servidor me contestó: {respuesta}")
          duration_time = end_time-start_time
          print(f"it completed in {duration_time} seconds.")
          

asyncio.run(conectar())