# manager.py
from pathlib import Path
import shutil
import datetime
import getpass
import os

# Assuming these are in the same package or sys.path is configured
# from .config import BackupConfig 
# from .discoverer import FileDiscoverer
# from .encryptor import FileEncryptor
# from .archiver import Archiver

class BackupManager:
    def __init__(self, config_path: str):
        # self.config = BackupConfig(config_path) # Simplified, assuming BackupConfig loads itself
        # For now, let's assume config is a dict for simplicity in this snippet
        # In a real app, BackupConfig would parse a file.
        # Example config structure for this snippet:
        self.config_data = {
            "backup_destination_path": "/tmp/my_backups/", # Make sure this exists
            "encryption_passphrase_prompt": True,
            "temporary_staging_path": "/tmp/my_backup_staging/",
            "archive_format": "tar.gz", # 'zip' or 'tar.gz'
            "files_to_include": [ # This would come from config.json
                {"type": "shell_history"},
                {"type": "ssh_keys"}
            ]
        }
        Path(self.config_data["backup_destination_path"]).mkdir(parents=True, exist_ok=True)


        self.discoverer = FileDiscoverer(config=self) # Pass self (manager) if discoverer needs get_setting
        
        passphrase = None
        if self.config_data.get("encryption_passphrase_prompt"):
            passphrase = getpass.getpass("Enter encryption passphrase: ")
            confirm_passphrase = getpass.getpass("Confirm encryption passphrase: ")
            if passphrase != confirm_passphrase:
                raise ValueError("Passphrases do not match.")
        # Add logic to get passphrase from a key file or environment variable
        
        if passphrase:
            self.encryptor = FileEncryptor(passphrase)
        else:
            self.encryptor = None # No encryption

        self.archiver = Archiver(archive_format=self.config_data.get("archive_format", "tar.gz"))
        self.staging_path = Path(self.config_data["temporary_staging_path"])

    # A helper to simulate BackupConfig's get_setting for FileDiscoverer
    def get_setting(self, key_name):
        return self.config_data.get(key_name)

    def _setup_staging_area(self) -> Path:
        if self.staging_path.exists():
            shutil.rmtree(self.staging_path)
        self.staging_path.mkdir(parents=True)
        print(f"Staging area created at: {self.staging_path}")
        return self.staging_path

    def _cleanup_staging_area(self):
        if self.staging_path.exists():
            shutil.rmtree(self.staging_path)
            print(f"Staging area cleaned up: {self.staging_path}")

    def run_backup(self):
        original_files = self.discoverer.discover_all_files()
        if not original_files:
            print("No files found to back up.")
            return

        self._setup_staging_area()
        
        staged_files_for_archive = []

        try:
            for original_file_path in original_files:
                # Create a relative path to preserve structure in staging and archive
                # For example, if original_file_path is /home/user/.bash_history
                # and you want to store it as .bash_history in the archive.
                # This needs careful thought: what's the "root" for your backup? Home? Filesystem root?
                # For simplicity, let's use the filename, or a predefined structure.
                # A good approach is to make paths relative to a common ancestor, e.g., Path.home()
                try:
                    relative_path = original_file_path.relative_to(Path.home())
                except ValueError: # If file is not under home, use its full path components
                    relative_path = Path(*original_file_path.parts[1:]) # Skips the leading '/'

                staged_file_dest_path = self.staging_path / relative_path
                staged_file_dest_path.parent.mkdir(parents=True, exist_ok=True)

                if self.encryptor:
                    print(f"Encrypting {original_file_path} to {staged_file_dest_path}")
                    self.encryptor.encrypt_file(original_file_path, staged_file_dest_path)
                else:
                    print(f"Copying {original_file_path} to {staged_file_dest_path}")
                    shutil.copy2(original_file_path, staged_file_dest_path)
                staged_files_for_archive.append(staged_file_dest_path)

            timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            archive_filename = f"backup-{timestamp}.{self.config_data.get('archive_format', 'tar.gz')}"
            # If you encrypt the WHOLE archive, you'd add .enc here.
            # The current design encrypts files individually *before* archiving.

            final_archive_path = Path(self.config_data["backup_destination_path"]) / archive_filename
            
            print(f"Compressing {len(staged_files_for_archive)} items to {final_archive_path}")
            self.archiver.compress_files(staged_files_for_archive, final_archive_path, self.staging_path)
            
            print(f"Backup successful! Archive created at: {final_archive_path}")

        finally:
            self._cleanup_staging_area()