import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image
from utils.github_utils import update_file, read_file
import io
from functools import lru_cache
import time
from config.settings import logger

# Constants
PLAYERS = [
    "Moti",
    "Chen",
    "Uri",
    "Baki",
    "Nir",
    "Asaf"
]

# File paths - these will be in your GitHub repo
GAMES_FILE = "data/games.csv"
PLAYERS_FILE = "data/players.csv"

# Add caching for data reads
@st.cache_data(ttl=60)
def read_games_data():
    """Read games data from GitHub with caching"""
    logger.debug("Reading games data from GitHub")
    games_content = read_file(GAMES_FILE)
    if games_content:
        logger.info("Successfully loaded games data")
        return pd.read_csv(io.StringIO(games_content))
    logger.warning("No games data found, creating empty DataFrame")
    return pd.DataFrame(columns=[
        'team1_player1', 'team1_player2', 'team2_player1', 'team2_player2',
        'team1_score', 'team2_score', 'date'
    ])

@st.cache_data(ttl=60)
def read_players_data():
    """Read players data from GitHub with caching"""
    logger.debug("Reading players data from GitHub")
    players_content = read_file(PLAYERS_FILE)
    if players_content:
        logger.info("Successfully loaded players data")
        players_df = pd.read_csv(io.StringIO(players_content))
        return players_df['name'].tolist()
    logger.warning("No players data found, using default players")
    return PLAYERS

# Modify the existing functions to use cached data
def init_data():
    """Initialize or load data from GitHub"""
    games_df = read_games_data()
    players = read_players_data()
    
    # Only write if data doesn't exist
    if games_df.empty:
        update_file(
            GAMES_FILE,
            games_df.to_csv(index=False),
            "Initialize games data"
        )
    
    if not players:
        players_df = pd.DataFrame({'name': PLAYERS})
        update_file(
            PLAYERS_FILE,
            players_df.to_csv(index=False),
            "Initialize players data"
        )
    
    return games_df, players

def add_game(team1_player1, team1_player2, team2_player1, team2_player2, team1_score, team2_score):
    logger.info(f"Adding new game: {team1_player1}/{team1_player2} vs {team2_player1}/{team2_player2}")
    games_df = read_games_data()
    
    new_game = pd.DataFrame([{
        'team1_player1': team1_player1,
        'team1_player2': team1_player2,
        'team2_player1': team2_player1,
        'team2_player2': team2_player2,
        'team1_score': team1_score,
        'team2_score': team2_score,
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }])
    games_df = pd.concat([new_game, games_df], ignore_index=True)
    
    success = update_file(
        GAMES_FILE,
        games_df.to_csv(index=False),
        f"Add game: {team1_player1}/{team1_player2} vs {team2_player1}/{team2_player2}"
    )
    if success:
        logger.info("Successfully added new game")
        read_games_data.clear()
        return True
    logger.error("Failed to add new game")
    return False

def get_recent_games(limit=5):
    games_df = read_games_data()
    return games_df.head(limit)

def get_rankings():
    games_df = read_games_data()
    
    if games_df.empty:
        return pd.DataFrame(columns=['games', 'wins', 'losses', 'draws', 'win_rate', 'points'])
    
    # Initialize rankings dictionary
    rankings = {}
    
    # Process each game
    for _, game in games_df.iterrows():
        # Team 1 players
        team1_players = [game['team1_player1'], game['team1_player2']]
        # Team 2 players
        team2_players = [game['team2_player1'], game['team2_player2']]
        
        # Initialize player stats if needed
        for player in team1_players + team2_players:
            if player not in rankings:
                rankings[player] = {'games': 0, 'wins': 0, 'losses': 0, 'draws': 0, 'points': 0}
        
        # Update stats for Team 1 players
        for player in team1_players:
            rankings[player]['games'] += 1
            if game['team1_score'] > game['team2_score']:
                rankings[player]['wins'] += 1
                rankings[player]['points'] += 3
            elif game['team1_score'] < game['team2_score']:
                rankings[player]['losses'] += 1
            else:
                rankings[player]['draws'] += 1
                rankings[player]['points'] += 1
        
        # Update stats for Team 2 players
        for player in team2_players:
            rankings[player]['games'] += 1
            if game['team2_score'] > game['team1_score']:
                rankings[player]['wins'] += 1
                rankings[player]['points'] += 3
            elif game['team2_score'] < game['team1_score']:
                rankings[player]['losses'] += 1
            else:
                rankings[player]['draws'] += 1
                rankings[player]['points'] += 1
    
    # Calculate win rate and convert to DataFrame
    for player, stats in rankings.items():
        # Win rate = wins / total games (as percentage)
        if stats['games'] > 0:
            win_rate = (stats['wins'] / stats['games']) * 100
            stats['win_rate'] = round(win_rate, 1)
            logger.debug(f"Player {player}: {stats['wins']} wins out of {stats['games']} games = {win_rate:.1f}%")
        else:
            stats['win_rate'] = 0.0
    
    rankings_df = pd.DataFrame.from_dict(rankings, orient='index')
    # Reorder columns to match display expectations
    rankings_df = rankings_df[['games', 'wins', 'losses', 'draws', 'win_rate', 'points']]
    # Sort by win rate first, then by total points as tiebreaker
    rankings_df = rankings_df.sort_values(['win_rate', 'points'], ascending=[False, False])
    return rankings_df

def get_players():
    return read_players_data()

def add_player(name):
    logger.info(f"Adding new player: {name}")
    players = read_players_data()
    if name in players:
        logger.warning(f"Player {name} already exists")
        return False
        
    players_df = pd.DataFrame({'name': players + [name]})
    success = update_file(
        PLAYERS_FILE,
        players_df.to_csv(index=False),
        f"Add player: {name}"
    )
    if success:
        logger.info(f"Successfully added player: {name}")
        read_players_data.clear()
        return True
    logger.error(f"Failed to add player: {name}")
    return False

def remove_player(name):
    logger.info(f"Removing player: {name}")
    players = read_players_data()
    if name not in players:
        logger.warning(f"Player {name} not found")
        return False
        
    players_df = pd.DataFrame({'name': [p for p in players if p != name]})
    success = update_file(
        PLAYERS_FILE,
        players_df.to_csv(index=False),
        f"Remove player: {name}"
    )
    if success:
        logger.info(f"Successfully removed player: {name}")
        read_players_data.clear()
        return True
    logger.error(f"Failed to remove player: {name}")
    return False

def reset_data():
    """Reset data files to initial state"""
    logger.warning("Resetting all data")
    
    # Reset players
    players_df = pd.DataFrame({'name': PLAYERS})
    players_success = update_file(
        PLAYERS_FILE,
        players_df.to_csv(index=False),
        "Reset players data"
    )
    
    # Reset games
    games_df = pd.DataFrame(columns=[
        'team1_player1', 'team1_player2', 'team2_player1', 'team2_player2',
        'team1_score', 'team2_score', 'date'
    ])
    games_success = update_file(
        GAMES_FILE,
        games_df.to_csv(index=False),
        "Reset games data"
    )
    
    if players_success and games_success:
        logger.info("Successfully reset all data")
    else:
        logger.error("Failed to reset some data")
    
    # Clear all caches
    read_games_data.clear()
    read_players_data.clear()

# Initialize data at startup
init_data()

# Initialize the app
st.title('FIFA Score Tracker')

# Create two columns for rankings and image
col1, col2 = st.columns([3, 1])  # 3:1 ratio for better layout

with col1:
    # 1. Display rankings (moved to top)
    st.subheader('Player Rankings')
    rankings = get_rankings()
    if not rankings.empty:
        # Reset index to show player names as a column
        rankings = rankings.reset_index()
        rankings.columns = ['Player', 'Games', 'Wins', 'Losses', 'Draws', 'Win Rate %', 'Points']
        st.dataframe(
            rankings,
            hide_index=True,
            column_config={
                "Player": st.column_config.TextColumn("Player", width="medium"),
                "Games": st.column_config.NumberColumn("Games", format="%d"),
                "Wins": st.column_config.NumberColumn("Wins", format="%d"),
                "Losses": st.column_config.NumberColumn("Losses", format="%d"),
                "Draws": st.column_config.NumberColumn("Draws", format="%d"),
                "Win Rate %": st.column_config.NumberColumn("Win Rate %", format="%.1f"),
                "Points": st.column_config.NumberColumn("Points", format="%d"),
            }
        )
    else:
        st.info('No games recorded yet')

with col2:
    # Display image
    try:
        # First try to load from assets directory
        image_path = "assets/images/14logo.png"
        if not os.path.exists(image_path):
            # If not found, try root directory
            image_path = "14logo.png"
        if os.path.exists(image_path):
            image = Image.open(image_path)
            st.image(image, use_container_width=True)
        else:
            st.error("Logo not found")
            logger.error(f"Logo not found in paths: assets/images/14logo.png or 14logo.png")
    except Exception as e:
        logger.error(f"Error loading logo: {e}")

# 2. Add new game form
st.subheader('Add New Game')
col1, col2 = st.columns(2)

players = get_players()

if len(players) < 4:
    st.warning("Please add at least 4 players to start recording games")
else:
    with col1:
        st.markdown("**Team 1**")
        team1_player1 = st.selectbox('Player 1', options=players, key='team1_p1')
        team1_player2_options = [p for p in players if p != team1_player1]
        team1_player2 = st.selectbox('Player 2', options=team1_player2_options, key='team1_p2')
        team1_score = st.number_input('Team 1 Score', min_value=0, max_value=20, value=0)

    with col2:
        st.markdown("**Team 2**")
        # Filter out Team 1 players
        team2_player_options = [p for p in players if p not in [team1_player1, team1_player2]]
        team2_player1 = st.selectbox('Player 1', options=team2_player_options, key='team2_p1')
        team2_player2_options = [p for p in team2_player_options if p != team2_player1]
        team2_player2 = st.selectbox('Player 2', options=team2_player2_options, key='team2_p2')
        team2_score = st.number_input('Team 2 Score', min_value=0, max_value=20, value=0)

    if st.button('Add Game'):
        if len({team1_player1, team1_player2, team2_player1, team2_player2}) == 4:
            add_game(team1_player1, team1_player2, team2_player1, team2_player2,
                    team1_score, team2_score)
            st.success('Game added successfully!')
            # Add rerun trigger
            st.rerun()
        else:
            st.error('Please select different players for each position')

# 3. Display recent games
st.subheader('Recent Games')
recent_games = get_recent_games()
if not recent_games.empty:
    # Format the date column
    recent_games['date'] = pd.to_datetime(recent_games['date']).dt.strftime('%Y-%m-%d %H:%M')
    recent_games.columns = ['Team 1 Player 1', 'Team 1 Player 2', 
                          'Team 2 Player 1', 'Team 2 Player 2',
                          'Team 1 Score', 'Team 2 Score', 'Date']
    st.dataframe(
        recent_games,
        hide_index=True,
        column_config={
            "Team 1 Player 1": st.column_config.TextColumn("Team 1 Player 1", width="medium"),
            "Team 1 Player 2": st.column_config.TextColumn("Team 1 Player 2", width="medium"),
            "Team 2 Player 1": st.column_config.TextColumn("Team 2 Player 1", width="medium"),
            "Team 2 Player 2": st.column_config.TextColumn("Team 2 Player 2", width="medium"),
            "Team 1 Score": st.column_config.NumberColumn("Team 1 Score", format="%d"),
            "Team 2 Score": st.column_config.NumberColumn("Team 2 Score", format="%d"),
            "Date": st.column_config.TextColumn("Date", width="medium"),
        }
    )
else:
    st.info('No games recorded yet')

# 4. Management sections at the bottom
st.markdown("---")  # Add a visual separator
st.subheader('Management')

# Database management
with st.expander("Database Management"):
    if st.button("Reset Database"):
        reset_data()
        st.success("Database reset successfully!")
        st.rerun()

# Player management
with st.expander("Manage Players"):
    col1, col2 = st.columns(2)
    
    with col1:
        new_player = st.text_input("Add new player")
        if st.button("Add Player"):
            if new_player:
                if add_player(new_player):
                    st.success(f"Added player: {new_player}")
                    st.rerun()
                else:
                    st.error("Player already exists")
            else:
                st.error("Please enter a player name")
    
    with col2:
        player_to_remove = st.selectbox(
            "Remove player",
            options=get_players(),
            key='remove_player'
        )
        if st.button("Remove Player"):
            remove_player(player_to_remove)
            st.success(f"Removed player: {player_to_remove}")
            st.rerun() 