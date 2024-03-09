import requests
from pathlib import Path


def get_secret_key(engine_pid):
    key_path = Path.home() / 'avaris' / 'instances' / engine_pid / 'secret.key'
    with open(key_path) as key_file:
        return key_file.read()


def send_command_to_engine(engine_pid, command_data):
    secret_key = get_secret_key(engine_pid)
    # Use the secret key for secure communication. This is a placeholder for illustration.
    response = requests.post(
        f"https://localhost:5001/command?secret={secret_key}",
        json=command_data,
        verify=False)
    print(response.json())


# Example command usage
engine_pid = '12345'  # Example PID; in practice, discover or let the user specify this
send_command_to_engine(engine_pid, {"action": "start_scraping"})
