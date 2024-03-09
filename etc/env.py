import os
from pathlib import Path

# Determine paths
script_path = Path(__file__).resolve()
working_dir = script_path.parent.parent
config = working_dir / "config"
data = working_dir / "data"
scrapers = working_dir / "scrapers"
logs = working_dir / "logs"
src = working_dir / "src"
plugins_executors = working_dir / ".avaris" / "src"
# Construct PYTHONPATH
pythonpath = f"{src}:{plugins_executors}"
# Environment variables to set in .env file
env_vars = {
    "WORKINGDIR": str(working_dir),
    "CONFIG": str(config),
    "SCRAPERS": str(scrapers),
    "DATA": str(data),
    "LOGS": str(logs),
    "SRC": str(src),
    "PYTHONPATH": str(pythonpath),
    "TIMEZONE": "UTC",
}
# Write to .env file
env_path = working_dir / ".env"
with env_path.open("w") as f:
    for key, value in env_vars.items():
        f.write(f"{key}={value}\n")

print(f"Environment variables set in {env_path}")
