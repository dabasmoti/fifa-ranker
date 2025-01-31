import os
from dotenv import load_dotenv
import logging

load_dotenv()

# GitHub settings
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_REPO = os.getenv('GITHUB_REPO')
GITHUB_BRANCH = "main"

# Logging settings
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
VALID_LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

# Configure logging
logging.basicConfig(
    level=VALID_LOG_LEVELS.get(LOG_LEVEL, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('fifa_tracker')

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