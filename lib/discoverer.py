# discoverer.py
from pathlib import Path
import os
from .config import BackupConfig

class FileDiscoverer:
    def __init__(self, config):
        self.config = config
        self.home_dir = Path.home()

    def get_shell_history_files(self) -> list[Path]:
        history_files = []
        common_files = [
            ".bash_history", ".zsh_history", ".fish_history",
            ".python_history", ".node_repl_history"
        ]
        for fname in common_files:
            fpath = self.home_dir / fname
            if fpath.exists() and fpath.is_file():
                history_files.append(fpath)
        
        
        histfile_env = os.environ.get('HISTFILE')
        if histfile_env:
            fpath_env = Path(histfile_env)
            if fpath_env.exists() and fpath_env.is_file() and fpath_env not in history_files:
                history_files.append(fpath_env)
                
        print(f"Discovered shell history files: {history_files}")
        return history_files

    def get_ssh_key_files(self) -> list[Path]:
        ssh_dir = self.home_dir / ".ssh"
        ssh_files = []
        if ssh_dir.is_dir():
            for item in ssh_dir.iterdir():
                if item.is_file():
                    ssh_files.append(item)
        print(f"Discovered SSH files: {ssh_files}")
        return ssh_files

    def get_gpg_key_files(self) -> list[Path]:
        gpg_dir = self.home_dir / ".gpg"
        gpg_files = []
        if gpg_dir.is_dir():
            for item in gpg_dir.iterdir():
                if item.is_file():
                    gpg_files.append(item)
        print(f"Discovered GPG files: {gpg_files}")
        return gpg_files

    def discover_all_files(self) -> list[Path]:
        all_files_to_backup = set()
        rules = self.config.get_setting("files_to_include")

        for rule in rules:
            if rule["type"] == "shell_history":
                all_files_to_backup.update(self.get_shell_history_files())
            elif rule["type"] == "ssh_keys":
                all_files_to_backup.update(self.get_ssh_key_files())
            elif rule["type"] == "gpg_keys":
                all_files_to_backup.update(self.get_gpg_key_files())
            elif rule["type"] == "custom_path":
                custom_p = Path(rule["path"]).expanduser()
                if custom_p.exists() and custom_p.is_file():
                    all_files_to_backup.add(custom_p)
                elif custom_p.is_dir():
                    print(f"Warning: Expected file for 'custom_path', got directory: {custom_p}. Use 'custom_directory' rule.")
            elif rule["type"] == "custom_directory":
                custom_d = Path(rule["path"]).expanduser()
                if custom_d.is_dir():
                    patterns = rule.get("patterns", ["*"]) # Default to all files if no pattern
                    recursive = rule.get("recursive", True)
                    for pattern in patterns:
                        if recursive:
                            all_files_to_backup.update(list(custom_d.rglob(pattern)))
                        else:
                            all_files_to_backup.update(list(custom_d.glob(pattern)))
        
        final_list = [f for f in all_files_to_backup if f.is_file()] # Ensure only files
        print(f"Total files discovered for backup: {len(final_list)}")
        return final_list