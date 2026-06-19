# speck/ssh/server.py
import asyncio
import asyncssh
import threading
import os


from .commands import cmd_agents, cmd_write


class SpeckSSHServer(asyncssh.SSHServer):
    def __init__(self, world):
        self._world = world

    def password_auth_supported(self):
        return True
    
    def validate_password(self, username, password):
        return True

    def session_requested(self):
        return SpeckSSHSession(self._world)


class SpeckSSHSession(asyncssh.SSHServerSession):
    def __init__(self, world):
        self._world = world
        self._input = ''

    def connection_made(self, chan):
        self._chan = chan
        self._chan.write('\r\n\r\n\r\nConnected to the Speck World Interface\r\n\r\n> ')

    def data_received(self, data, datatype):
        self._input += data
        if '\n' in self._input:
            line, self._input = self._input.split('\n', 1)
            self._handle_command(line.strip())

    def shell_requested(self):
        return True

    def _handle_command(self, line):
        if line == 'agents':
            self._chan.write(cmd_agents(self._world) + '\r\n> ')
        elif line.startswith('write '):
            parts = line.split(' ', 2)
            if len(parts) == 3:
                self._chan.write(cmd_write(self._world, parts[1], parts[2]) + '\r\n> ')
            else:
                self._chan.write('usage: write <key> <value>\r\n> ')
        elif line == 'help':
            self._chan.write('commands: agents, write <key> <value>, help\r\n> ')
        elif line in ('exit', 'quit'):
            self._chan.write('Goodbye.\r\n')
            self._chan.close()
        else:
            self._chan.write(f'unknown command: {line}\r\n> ')

    def eof_received(self):
        self._chan.close()


def start_ssh_server(world, host='127.0.0.1', port=2222):
    def run():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def _start():
            key_path = 'speck_host_key'
            if os.path.exists(key_path):
                host_key = asyncssh.read_private_key(key_path)
            else:
                host_key = asyncssh.generate_private_key('ssh-ed25519')
                host_key.write_private_key(key_path)
            
            await asyncssh.create_server(
                lambda: SpeckSSHServer(world),
                host, port,
                server_host_keys=[host_key],
            )
            await loop.create_future()

        loop.run_until_complete(_start())

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    print(f"SSH server started on {host}:{port}")