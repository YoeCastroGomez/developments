# Requisitos pendientes : Backend de Teleoperación

Lista de lo que se necesita para avanzar a las siguientes fases del [Plan Técnico](tecnical_plan_teleop.md) (relay, seguridad calibrada, integración con hardware real y con el Pico VR).

---

## 1. Servidor en la nube (para el Relay : Fase 7)

No necesita ser potente: el relay solo reenvía mensajes entre el operador y el robot, no hace cálculos pesados. La opción más barata (o gratis) alcanza de sobra.

| Opción | Costo | Nota |
|---|---|---|
| **Oracle Cloud "Always Free"** | Gratis permanente | Recomendada: da una VM chica gratis para siempre (no es una prueba de 12 meses). Pide tarjeta para verificar identidad, pero no cobra si te quedas en el tier gratuito. |
| **Google Cloud (e2-micro)** | Gratis permanente (con límites de horas/región) | Alternativa gratis, algo más restringida en región. |
| **DigitalOcean / Vultr / Linode** | ~$4–6 USD/mes | Las más simples de configurar y documentar; no depende de letra chica de un "tier gratis". |
| **AWS Free Tier** | Gratis solo 12 meses | Después empieza a cobrar, evitar si no van a estar pendientes de cancelarlo. |

**Pedido concreto:** aprobación para levantar un VPS en Oracle Cloud (Always Free) o, si se prefiere simplicidad sobre costo cero, un droplet de DigitalOcean de ~$4-6/mes.

---

## 2. Acceso SSH a la máquina conectada al robot

Necesario para poder instalar y correr el servidor de control (`remote_server.py`) directo en la máquina que tiene el cable/conexión al robot, y probarlo con hardware real.

### ¿Qué es SSH?

Es una forma de manejar otra computadora a distancia por terminal (como si estuvieras sentado frente a ella), de forma segura. No es una app que se "descarga": es un servicio que corre en la máquina del robot, y alguien tiene que habilitártelo y darte credenciales.

### Cómo conseguirlo (pasos concretos para pedir)

1. **Generar tu propia llave SSH** (no pidas que te den una contraseña, es más seguro con llave):
   ```bash
   ssh-keygen -t ed25519 -C "tu_nombre@handumi"
   ```
   Esto te crea un archivo `.pub` (llave pública, la que compartes) y uno privado (nunca se comparte).

2. Solicitar:
   - Cree un usuario en esa máquina (o confirme cuál usuario vas a usar).
   - Agregue tu **llave pública** (`archivo .pub`, el contenido de texto) al archivo `authorized_keys` de ese usuario en la máquina del robot.
   - Confirme que el **servicio SSH esté activo** en esa máquina (en Linux normalmente ya viene activo; en Windows hay que habilitar "OpenSSH Server" desde configuración).
   - Te dé la **IP o nombre de red** de la máquina, y el **puerto** si no es el 22 por defecto.

3. **Verificar que puedas alcanzar esa IP** desde donde vayas a trabajar. Si la máquina está en una red interna y te vas a conectar desde afuera, vas a necesitar además una VPN (confirmar si existe una).

**Pedido :** "Necesito que me den acceso SSH a la máquina conectada al robot: que agreguen mi llave pública (te la mando), me confirmen usuario e IP, y si hace falta VPN para llegar a esa red desde afuera."

---

## 3. Ficha técnica del robot

Esto alimenta directo el filtro de seguridad (`SafetyGate`), que todavía está sin construir (stub: por ahora permite cualquier movimiento). Hace falta esta ficha técnica para implementar los límites de rango y velocidad de verdad.

- **Grados de libertad (DOF)** de cada brazo: cuántas articulaciones tiene realmente.
- **Rango de movimiento por articulación** (mínimo/máximo en grados).
- **Velocidad/aceleración máxima segura** por articulación: para calibrar el salto máximo permitido entre comandos.
- **Protocolo de comunicación del actuador**: ¿serial/USB, CAN bus, Ethernet, SDK propietario? Define cómo se escribe el driver real.
- **Procedimiento de parada de emergencia física**: si el robot tiene un e-stop de hardware (botón/relé), cómo se activa y cómo el software debe enterarse de eso.

---

## 4. Sobre el Pico VR

- Confirmar si ya existe una **cuenta de desarrollador Pico** (necesaria para acceder al SDK y poder compilar/instalar apps propias en el dispositivo, no solo usarlo como consumidor).
- Disponibilidad de al menos un headset/controladores físicos para empezar a probar el cliente VR.

---

## 5. Detalle operativo / red

- Confirmar que la red donde va a estar el robot **permite conexiones salientes** (normalmente sí, pero vale confirmarlo : el relay depende de que ambos lados puedan "llamar hacia afuera").
- Quién es la persona autorizada a operar el robot real una vez conectado (tema de seguridad, no técnico, pero es esperable que lo pregunten).

---

## Resumen

1. Aprobación para un VPS barato o gratis (relay).
2. Acceso SSH a la máquina del robot (llave pública, usuario, IP, VPN si aplica).
3. Ficha técnica del actuador (límites de movimiento y protocolo de comunicación).
4. Estado de la cuenta de desarrollador Pico y disponibilidad del hardware VR.
