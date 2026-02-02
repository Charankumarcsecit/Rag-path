"""Handlers for different upload sources (GitHub, Drive, etc.)."""

import os
import logging
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import List, Optional
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GitHubRepoHandler:
    """Handle cloning and processing GitHub repositories."""
    
    @staticmethod
    def clone_repo(repo_url: str, target_dir: Optional[Path] = None) -> Optional[Path]:
        """
        Clone a GitHub repository.
        
        Args:
            repo_url: GitHub repository URL
            target_dir: Target directory (if None, uses temp directory)
            
        Returns:
            Path to cloned repository or None if failed
        """
        try:
            if target_dir is None:
                target_dir = Path(tempfile.mkdtemp(prefix="github_repo_"))
            
            # Clean the URL
            if not repo_url.startswith(('http://', 'https://')):
                repo_url = f'https://github.com/{repo_url}'
            
            if not repo_url.endswith('.git'):
                repo_url = f'{repo_url}.git'
            
            logger.info(f"Cloning repository: {repo_url}")
            
            # Use git command to clone
            subprocess.run(
                ['git', 'clone', '--depth', '1', repo_url, str(target_dir)],
                check=True,
                capture_output=True,
                text=True
            )
            
            logger.info(f"Successfully cloned to {target_dir}")
            return target_dir
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error cloning repository: {e.stderr}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error cloning repository: {e}")
            return None


class GoogleDriveHandler:
    """Handle downloading files from Google Drive."""
    
    @staticmethod
    def extract_file_id(drive_url: str) -> Optional[str]:
        """Extract file ID from Google Drive URL."""
        # Handle different Drive URL formats
        if '/file/d/' in drive_url:
            return drive_url.split('/file/d/')[1].split('/')[0]
        elif 'id=' in drive_url:
            return drive_url.split('id=')[1].split('&')[0]
        elif '/open?id=' in drive_url:
            return drive_url.split('/open?id=')[1].split('&')[0]
        return None
    
    @staticmethod
    def download_file(drive_url: str, output_path: Optional[Path] = None) -> Optional[Path]:
        """
        Download a file from Google Drive.
        
        Args:
            drive_url: Google Drive sharing URL
            output_path: Output file path (if None, uses temp file)
            
        Returns:
            Path to downloaded file or None if failed
        """
        try:
            file_id = GoogleDriveHandler.extract_file_id(drive_url)
            if not file_id:
                logger.error("Could not extract file ID from Drive URL")
                return None
            
            # Google Drive direct download URL
            download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
            
            logger.info(f"Downloading from Google Drive: {file_id}")
            
            session = requests.Session()
            response = session.get(download_url, stream=True)
            
            # Handle large file confirmation
            for key, value in response.cookies.items():
                if key.startswith('download_warning'):
                    params = {'id': file_id, 'confirm': value}
                    response = session.get(download_url, params=params, stream=True)
            
            if output_path is None:
                # Try to get filename from headers
                content_disposition = response.headers.get('content-disposition', '')
                if 'filename=' in content_disposition:
                    filename = content_disposition.split('filename=')[1].strip('"')
                else:
                    filename = f"drive_file_{file_id}"
                
                output_path = Path(tempfile.gettempdir()) / filename
            
            # Download the file
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=32768):
                    if chunk:
                        f.write(chunk)
            
            logger.info(f"Successfully downloaded to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error downloading from Google Drive: {e}")
            return None
    
    @staticmethod
    def download_folder(drive_url: str) -> Optional[Path]:
        """
        Download a folder from Google Drive (requires gdrive or rclone).
        
        Args:
            drive_url: Google Drive folder sharing URL
            
        Returns:
            Path to downloaded folder or None if failed
        """
        logger.warning("Google Drive folder download requires additional setup (gdrive/rclone)")
        logger.info("For now, please download the folder manually or share individual files")
        return None


class DropboxHandler:
    """Handle downloading files from Dropbox."""
    
    @staticmethod
    def download_file(dropbox_url: str, output_path: Optional[Path] = None) -> Optional[Path]:
        """
        Download a file from Dropbox.
        
        Args:
            dropbox_url: Dropbox sharing URL
            output_path: Output file path (if None, uses temp file)
            
        Returns:
            Path to downloaded file or None if failed
        """
        try:
            # Convert sharing URL to direct download URL
            if 'www.dropbox.com' in dropbox_url:
                download_url = dropbox_url.replace('www.dropbox.com', 'dl.dropboxusercontent.com')
                if '?dl=0' in download_url:
                    download_url = download_url.replace('?dl=0', '?dl=1')
                elif 'dl=' not in download_url:
                    download_url += '?dl=1'
            else:
                download_url = dropbox_url
            
            logger.info(f"Downloading from Dropbox")
            
            response = requests.get(download_url, stream=True)
            response.raise_for_status()
            
            if output_path is None:
                # Try to get filename from URL
                filename = dropbox_url.split('/')[-1].split('?')[0]
                output_path = Path(tempfile.gettempdir()) / filename
            
            # Download the file
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=32768):
                    if chunk:
                        f.write(chunk)
            
            logger.info(f"Successfully downloaded to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error downloading from Dropbox: {e}")
            return None
