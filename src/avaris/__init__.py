import os
from dotenv import load_dotenv
def ensure_env_variables():
    """
    Ensure key environment variables are set, using default values if necessary.
    """
    # Load the environment variables from .env file
    load_dotenv()
    # Define the key environment variables to check and their default values
    key_env_vars = ["WORKINGDIR", "DATA", "PYTHONPATH", "CONFIG", "LOGS", "COMPENDIUM"]

    # Set environment variables to "" if they are not already set
    for var in key_env_vars:
        if not os.getenv(var):
            os.environ[var] = ""
            continue
        #print(f"[.env] {var} : {os.getenv(var)}")

ensure_env_variables()