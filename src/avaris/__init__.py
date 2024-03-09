from pathlib import Path
import dotenv

base_dir = Path(__file__).resolve().parent.parent.parent
dotenv_path = base_dir / ".env"
dotenv_path = dotenv_path if dotenv_path.exists() else Path().cwd() / ".env"
if dotenv.load_dotenv(dotenv_path=dotenv_path):
    print(f"Loaded .env from: {dotenv_path}")