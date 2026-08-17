## Phase 7: relay / connectivity between different networks.
## Public relay server: pairs an operator and a robot node by session_id and
## forwards messages between them without interpreting the content (see
## "4.2 Por que el relay es necesario" in tecnical_plan_teleop.md).
## Local testing only for now: still needs to be deployed on a VPS with a
## public IP to actually connect two different networks.

import asyncio
import websockets

ROLES = ("operator", "robot")


class RelaySession:
    """Holds the two peers (operator, robot) that share one session_id."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.peers = {}  ## role -> websocket

    def add(self, role: str, websocket):
        self.peers[role] = websocket

    def remove(self, role: str):
        self.peers.pop(role, None)

    def other_role(self, role: str) -> str:
        return "robot" if role == "operator" else "operator"

    def peer_of(self, role: str):
        return self.peers.get(self.other_role(role))

    def is_empty(self) -> bool:
        return not self.peers


class Relay:
    """Pairs clients by session_id and forwards messages between the two
    peers of each session, without interpreting them."""

    def __init__(self):
        self.sessions: dict[str, RelaySession] = {}

    def _session_for(self, session_id: str) -> RelaySession:
        if session_id not in self.sessions:
            self.sessions[session_id] = RelaySession(session_id)
        return self.sessions[session_id]

    async def register(self, websocket):
        """Reads the first message, expected as 'REGISTER,<role>,<session_id>'.
        Returns (role, session_id) on success, None on invalid registration."""
        try:
            message = await websocket.recv()
            _, role, session_id = message.split(",")
            role = role.strip()
            session_id = session_id.strip()
        except (ValueError, websockets.ConnectionClosed):
            await self._safe_send(websocket, "Invalid registration. Use 'REGISTER,<role>,<session_id>' (role in operator/robot).")
            return None

        if role not in ROLES:
            await self._safe_send(websocket, f"Unknown role '{role}'. Use one of {ROLES}.")
            return None

        session = self._session_for(session_id)
        if role in session.peers:
            await self._safe_send(websocket, f"Role '{role}' already connected for session '{session_id}'.")
            return None

        session.add(role, websocket)
        await self._safe_send(websocket, f"REGISTERED as '{role}' in session '{session_id}'.")

        peer = session.peer_of(role)
        if peer is not None:
            await self._safe_send(peer, f"PEER_CONNECTED: '{role}' joined session '{session_id}'.")

        return role, session_id

    async def handle_connection(self, websocket):
        registration = await self.register(websocket)
        if registration is None:
            await websocket.close()
            return

        role, session_id = registration
        session = self.sessions[session_id]

        try:
            async for message in websocket:
                peer = session.peer_of(role)
                if peer is None:
                    await self._safe_send(websocket, "Peer not connected yet, message dropped.")
                    continue
                await self._safe_send(peer, message)  ## forwarded as-is, relay never interprets it
        finally:
            session.remove(role)
            peer = session.peer_of(role)
            if peer is not None:
                await self._safe_send(peer, f"PEER_DISCONNECTED: '{role}' left session '{session_id}'.")
            if session.is_empty():
                self.sessions.pop(session_id, None)

    @staticmethod
    async def _safe_send(websocket, message: str):
        try:
            await websocket.send(message)
        except websockets.ConnectionClosed:
            pass


async def main():
    print("Relay listening on port 8766...")
    relay = Relay()
    async with websockets.serve(relay.handle_connection, "localhost", 8766):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
