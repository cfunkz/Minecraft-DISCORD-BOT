import json
from dotenv import load_dotenv
import os

IP = "82.165.63.11"
PORT = 25565
# Load environment variables from the .env file
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
RCON_PASSWORD = os.getenv("RCON_PASSWORD")
RCON_PORT = int(os.getenv("RCON_PORT", 25575))
RCON_HOST = os.getenv("RCON_HOST")

#DISCORD_TOKEN = ""
#RCON_PASSWORD = ""
#RCON_PORT = 25575
#RCON_HOST = ""

ADMIN_ROLES_FILE = "admin_roles.json"

def load_admin_roles():
    try:
        with open(ADMIN_ROLES_FILE, "r") as file:
            data = json.load(file)
            return data["allowed_role_ids"]
    except FileNotFoundError:
        print(f"{ADMIN_ROLES_FILE} not found. Creating a new one...")
        default_data = {"allowed_role_ids": []}
        save_admin_roles(default_data["allowed_role_ids"])
        return default_data["allowed_role_ids"]
    except json.JSONDecodeError:
        print(f"Error reading {ADMIN_ROLES_FILE}. Check the file format.")
        return []

def save_admin_roles(allowed_role_ids):
    with open(ADMIN_ROLES_FILE, "w") as file:
        json.dump({"allowed_role_ids": allowed_role_ids}, file, indent=4)

ALLOWED_ROLE_ID = load_admin_roles()
