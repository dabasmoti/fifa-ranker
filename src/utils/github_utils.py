from github import Github
import os
import base64
from dotenv import load_dotenv

load_dotenv()

# GitHub settings
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
REPO_NAME = os.getenv('GITHUB_REPO')  # format: "username/repository"
BRANCH = "main"  # or whatever branch you want to use

def get_github_client():
    return Github(GITHUB_TOKEN)

def update_file(file_path, content, commit_message):
    """Update file in GitHub repository"""
    try:
        g = get_github_client()
        repo = g.get_repo(REPO_NAME)
        
        # Try to get the file first
        try:
            file = repo.get_contents(file_path, ref=BRANCH)
            repo.update_file(
                file_path,
                commit_message,
                content,
                file.sha,
                branch=BRANCH
            )
        except Exception:
            # File doesn't exist, create it
            repo.create_file(
                file_path,
                commit_message,
                content,
                branch=BRANCH
            )
        return True
    except Exception as e:
        print(f"Error updating file: {e}")
        return False

def read_file(file_path):
    """Read file from GitHub repository"""
    try:
        g = get_github_client()
        repo = g.get_repo(REPO_NAME)
        file = repo.get_contents(file_path, ref=BRANCH)
        content = base64.b64decode(file.content).decode('utf-8')
        return content
    except Exception as e:
        print(f"Error reading file: {e}")
        return None 