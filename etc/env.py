import os
from pathlib import Path

# Determine paths
script_path = Path(__file__).resolve()
working_dir = script_path.parent.parent
config = working_dir / "config" / "conf.yaml"
data = working_dir / "data"
compendium = working_dir / "compendium"
logs = working_dir / "logs"
src = working_dir / "src"
plugins_executors = working_dir / ".avaris" / "src"
# Construct PYTHONPATH
pythonpath = f"{src}:{plugins_executors}"
debug = False
# Environment variables to set in .env file
env_vars = {
    "WORKINGDIR": str(working_dir),
    "CONFIG": str(config),
    "COMPENDIUM": str(compendium),
    "DATA": str(data),
    "LOGS": str(logs),
    "PYTHONPATH": str(pythonpath),
    "TIMEZONE": "UTC",
    "DEBUG": debug,
}
# Write to .env file
env_path = working_dir / ".env"
with env_path.open("w") as f:
    for key, value in env_vars.items():
        f.write(f"{key}={value}\n")

print(f"Dev Environment variables set in {env_path}")
