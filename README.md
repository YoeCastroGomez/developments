# API Remote Teleop (own)

Backend de teleoperación remota para un robot **de dos brazos** (cada brazo es una mano robótica independiente). Es un **prototipo/PoC**: expone un servidor WebSocket que recibe comandos de movimiento de un operador remoto, decide si ese movimiento se puede ejecutar (según un árbitro de seguridad tipo e-stop) y lo aplica sobre el brazo indicado. Hoy los brazos se simulan con física real en PyBullet (abre una ventana con dos brazos Kuka IIWA al arrancar el servidor).

> Para el roadmap por fases, la arquitectura completa (relay, SafetyGate, grabación de sesiones) y las decisiones de diseño, ver el [Plan Técnico](tecnical_plan_teleop.md).

## Qué hace

1. Un operador (cliente) se conecta por WebSocket al servidor. Una sesión = una conexión = control de **ambos brazos** del robot.
2. Envía comandos con el formato `arm_id,joint_id,position` (ej. `left,2,45`, con `arm_id` en `{"left","right"}`) o comandos especiales `ESTOP` / `RESET`.
3. El servidor mantiene un estado de sesión (`operator_connected`, `estop_activated`) y le pasa ese estado a un **árbitro** (`Arbiter`), que decide la fuente de movimiento permitida en ese instante:
   - `ESTOP` → bloquea cualquier movimiento (parada de emergencia activa, afecta a los dos brazos).
   - `TELEOP` → hay operador conectado y no hay e-stop → se ejecuta el movimiento sobre el brazo indicado.
   - `HOLD` → no hay operador conectado → no se permite mover ningún brazo.

   **Decisión de diseño:** el e-stop es **global a la sesión, no por brazo**. Un solo `ESTOP` detiene los dos brazos a la vez, igual que un botón físico de emergencia real. Se descartó a propósito un e-stop independiente por brazo para no arriesgar que un brazo se siga moviendo mientras el otro está "parado".
4. El robot se modela como **dos instancias independientes** de `RobotPyBullet` (una por brazo, `"left"` y `"right"`, en posiciones distintas dentro del mismo mundo físico de PyBullet), cada una con sus propias articulaciones; cada instancia actualiza y devuelve su propio estado.
5. El servidor responde al cliente por el mismo socket con el resultado (brazo + estado, error de formato, brazo desconocido, o mensaje de bloqueo por e-stop).

`RobotFakeHand` (mock sin física, solo actualiza números en memoria) fue el robot original de la Fase 1 y sigue en el repo, pero ya no lo usa `remote_server.py`. `sim_test.py`, el script suelto que precedió a `robot_py_bullet_sim.py`, tampoco está conectado al servidor (ese sí, `robot_py_bullet_sim.py`, es el que usa el servidor hoy).

## Tecnologías usadas

- **Python 3.13** (asyncio nativo).
- **[`websockets`](https://websockets.readthedocs.io/)**: servidor y cliente WebSocket (comunicación bidireccional en tiempo real entre operador y robot).
- **`asyncio`**: manejo concurrente de conexiones/mensajes.
- **`enum`**: modelado del estado de la fuente de movimiento (`MovementSource`).
- **[`pybullet`](https://pybullet.org/)** + `pybullet_data`: simulación física 3D del robot (motor de físicas + GUI), usado para probar movimientos de articulaciones sin hardware real.

No hay framework HTTP (Flask/FastAPI) ni base de datos; todo el estado vive en memoria del proceso del servidor.

## Estructura de archivos

| Archivo | Rol | Estado |
|---|---|---|
| [`remote_server.py`](remote_server.py) | Servidor WebSocket principal (`Server_Teleop`). Orquesta conexión, parsing de comandos (`arm_id,joint_id,position`), e-stop y llamadas al brazo correspondiente. Mantiene `self.robots = {"left": RobotPyBullet, "right": RobotPyBullet}`. | Funcional (PoC) |
| [`arbiter.py`](arbiter.py) | `Arbiter` + `MovementSource`: decide si el movimiento se permite (ESTOP / TELEOP / HOLD) según el estado del operador y del e-stop. Decisión global de sesión, no por brazo. | Funcional, con script de prueba manual al final del propio archivo |
| [`fake_robot_hand.py`](fake_robot_hand.py) | `RobotFakeHand`: mock de **una** mano/brazo robótico de 5 articulaciones (`joint_positions`), con un `name` (`"left"`/`"right"`) para identificarla en logs. Robot original de la Fase 1. | Funcional como mock, pero ya no lo usa `remote_server.py` (reemplazado por `RobotPyBullet`) |
| [`prove_client.py`](prove_client.py) | Cliente CLI de prueba: se conecta al servidor y permite mandar comandos a mano por consola (`arm_id,joint_id,position`), mide latencia. | Funcional (herramienta de prueba manual) |
| [`robot_py_bullet_sim.py`](robot_py_bullet_sim.py) | `RobotPyBullet`: clase que envuelve la simulación en PyBullet de **un** brazo Kuka IIWA (setup de escena, conversión grados→radianes, mover una articulación). | Integrada con `remote_server.py`, dos instancias (una por brazo) comparten el mismo mundo físico |
| [`sim_test.py`](sim_test.py) | Script suelto de prueba de PyBullet (versión no orientada a objetos de `robot_py_bullet_sim.py`, con loop de simulación). | Script de prueba/duplicado, no forma parte del flujo del servidor |
| [`relay/relay.py`](relay/relay.py) | `Relay`: servidor WebSocket que empareja operador y nodo del robot por `session_id` (protocolo `REGISTER,<role>,<session_id>`) y reenvía mensajes entre ambos sin interpretarlos. | Funcional en local, falta desplegarlo en un VPS con IP pública y conectarlo al flujo de `remote_server.py` |

## Qué falta por construir

A alto nivel: capa de seguridad de rangos/velocidad (SafetyGate, sin implementar todavía), despliegue del relay en un VPS con IP pública y su conexión al flujo del servidor, grabación de sesiones, integración con hardware real, y lo esperable de un backend productivo (config externa, logging, auth/cifrado, reconexión, `requirements.txt`, tests automatizados).

El detalle de cada fase, su estado y el orden en que se van a atacar está en el [Plan Técnico](tecnical_plan_teleop.md#5-fases-del-proyecto). Esa es la fuente de verdad del roadmap, para no duplicarlo aquí.

## Cómo probarlo hoy (manual)

```bash
# Terminal 1: levantar el servidor (abre una ventana de PyBullet con los dos brazos)
python remote_server.py

# Terminal 2: cliente interactivo
python prove_client.py
# escribir, por ejemplo: left,2,45   (mueve el brazo izquierdo)
#                         right,0,90 (mueve el brazo derecho)
# o: ESTOP  /  RESET
```

> Requiere `pybullet` instalado y un entorno con pantalla (`p.connect(p.GUI)` abre una ventana; no corre en modo headless tal como está).
