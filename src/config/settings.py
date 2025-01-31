import os
from dotenv import load_dotenv

load_dotenv()

# GitHub settings
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_REPO = os.getenv('GITHUB_REPO')
GITHUB_BRANCH = "main"

# File paths
DATA_DIR = "data"
GAMES_FILE = f"{DATA_DIR}/games.csv"
PLAYERS_FILE = f"{DATA_DIR}/players.csv"

# Default players
PLAYERS = [
    "Moti",
    "Chen",
    "Uri",
    "Baki",
    "Nir",
    "Asaf"
] 