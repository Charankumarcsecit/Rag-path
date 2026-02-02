"""Git repository monitoring for real-time documentation updates."""

import os
import time
import logging
from pathlib import Path
from typing import List, Optional
import git
from git import Repo, GitCommandError

import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GitWatcher:
    """Monitors a Git repository for changes and pulls updates."""
    
    def __init__(self, repo_url: str, local_path: Path):
        """
        Initialize the Git watcher.
        
        Args:
            repo_url: URL of the Git repository to monitor
            local_path: Local path where the repository will be cloned
        """
        self.repo_url = repo_url
        self.local_path = local_path
        self.repo: Optional[Repo] = None
        
    def setup(self) -> bool:
        """
        Clone or open the repository.
        
        Returns:
            True if setup successful, False otherwise
        """
        try:
            if self.local_path.exists() and (self.local_path / ".git").exists():
                logger.info(f"Opening existing repository at {self.local_path}")
                self.repo = Repo(self.local_path)
            elif self.repo_url:
                logger.info(f"Cloning repository from {self.repo_url}")
                self.local_path.mkdir(parents=True, exist_ok=True)
                self.repo = Repo.clone_from(self.repo_url, self.local_path)
            else:
                logger.error(f"No existing repository at {self.local_path} and no URL provided")
                return False
            
            logger.info(f"Repository setup complete. Current branch: {self.repo.active_branch}")
            return True
            
        except GitCommandError as e:
            logger.error(f"Git error during setup: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during setup: {e}")
            return False
    
    def check_for_updates(self) -> bool:
        """
        Check if there are updates in the remote repository.
        
        Returns:
            True if updates are available, False otherwise
        """
        if not self.repo:
            logger.warning("Repository not initialized")
            return False
            
        try:
            # Fetch latest changes
            origin = self.repo.remotes.origin
            origin.fetch()
            
            # Compare local and remote commits
            local_commit = self.repo.head.commit
            remote_commit = origin.refs[self.repo.active_branch.name].commit
            
            return local_commit != remote_commit
            
        except Exception as e:
            logger.error(f"Error checking for updates: {e}")
            return False
    
    def pull_updates(self) -> bool:
        """
        Pull latest changes from the remote repository.
        
        Returns:
            True if pull successful, False otherwise
        """
        if not self.repo:
            logger.warning("Repository not initialized")
            return False
            
        try:
            origin = self.repo.remotes.origin
            pull_info = origin.pull()
            
            if pull_info:
                logger.info(f"Successfully pulled updates: {pull_info[0].commit.hexsha[:7]}")
                return True
            return False
            
        except GitCommandError as e:
            logger.error(f"Git error during pull: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during pull: {e}")
            return False
    
    def get_changed_files(self) -> List[str]:
        """
        Get list of files that changed in the last commit.
        
        Returns:
            List of changed file paths
        """
        if not self.repo:
            return []
            
        try:
            # Get the diff between HEAD and HEAD~1
            if len(list(self.repo.iter_commits())) < 2:
                # If only one commit, return all tracked files
                return [item.path for item in self.repo.tree().traverse()]
            
            head_commit = self.repo.head.commit
            prev_commit = head_commit.parents[0] if head_commit.parents else None
            
            if prev_commit:
                diffs = prev_commit.diff(head_commit)
                changed_files = [diff.a_path for diff in diffs]
                return changed_files
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting changed files: {e}")
            return []
    
    def watch(self, callback=None, interval: int = 30):
        """
        Continuously watch the repository for changes.
        
        Args:
            callback: Function to call when changes are detected
            interval: Polling interval in seconds
        """
        logger.info(f"Starting to watch repository every {interval} seconds")
        
        while True:
            try:
                if self.check_for_updates():
                    logger.info("Updates detected! Pulling changes...")
                    if self.pull_updates():
                        changed_files = self.get_changed_files()
                        logger.info(f"Changed files: {changed_files}")
                        
                        if callback:
                            callback(changed_files)
                
                time.sleep(interval)
                
            except KeyboardInterrupt:
                logger.info("Stopping Git watcher")
                break
            except Exception as e:
                logger.error(f"Error in watch loop: {e}")
                time.sleep(interval)


def main():
    """Test the Git watcher."""
    if not config.DOCS_REPO_URL:
        logger.error("DOCS_REPO_URL not configured in .env file")
        return
    
    watcher = GitWatcher(config.DOCS_REPO_URL, config.DOCS_REPO_PATH)
    
    if watcher.setup():
        def on_change(files):
            print(f"Files changed: {files}")
        
        watcher.watch(callback=on_change, interval=config.GIT_POLL_INTERVAL)


if __name__ == "__main__":
    main()
