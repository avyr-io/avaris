import os
from pathlib import Path
import secrets


def generate_and_store_keys(pid):
    secret_key = secrets.token_hex(
        16)  # Generates a secure 32-character hexadecimal string
    instance_dir = Path.home() / 'avaris' / 'instances' / str(pid)
    instance_dir.mkdir(parents=True, exist_ok=True)
    with open(instance_dir / 'secret.key', 'w') as key_file:
        key_file.write(secret_key)


# Example usage within the engine startup process
engine_pid = os.getpid()
secret_key = generate_and_store_keys(engine_pid)
