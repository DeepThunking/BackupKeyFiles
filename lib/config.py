# lib/config.py
import json
from pathlib import Path
import sys

# Define default settings that will be used if not specified in the config file
# or if the config file is missing.
DEFAULT_CONFIG = {
    "backup_destination_path": str(Path.home() / "backups" / "my_system_backup"),
    "encryption_enabled": True,
    "encryption_passphrase_prompt": True,
    "encryption_key_path": None,  # Alternative to passphrase prompt, path to a file containing the key/passphrase
    "temporary_staging_path": "/tmp/backup_utility_staging",
    "archive_format": "tar.gz",  # Supported: "tar.gz", "zip"
    "log_file_path": str(Path.home() / ".local" / "state" / "backup_utility" / "backup.log"),
    "log_level": "INFO",  # CRITICAL, ERROR, WARNING, INFO, DEBUG
    "files_to_include": [
        {
            "type": "shell_history",
            "enabled": True,
            "details": "Backs up common shell history files (.bash_history, .zsh_history, etc.)"
        },
        {
            "type": "ssh_keys",
            "enabled": True,
            "include_private_keys": True,
            "include_public_keys": True,
            "include_known_hosts": True,
            "include_config_file": True, # for ~/.ssh/config
            "details": "Backs up SSH keys and related configuration from ~/.ssh/"
        },
        # --- Add more predefined rule types or examples for custom rules below ---
        # Example:
        # {
        #   "type": "custom_path",
        #   "path": "~/.gitconfig", # Specific file
        #   "enabled": True,
        #   "details": "User's global Git configuration."
        # },
        # {
        #   "type": "custom_directory",
        #   "path": "~/Documents/important_notes", # Specific directory
        #   "patterns": ["*.txt", "*.md"], # List of glob patterns
        #   "recursive": True,
        #   "enabled": True,
        #   "details": "Important notes from a specific directory."
        # }
    ]
}

class BackupConfig:
    """
    Manages loading and accessing configuration settings for the backup utility.
    Settings are loaded from a JSON file, with defaults provided.
    """
    def __init__(self, config_file_path: str | Path = "config.json"):
        """
        Initializes the BackupConfig instance.

        Args:
            config_file_path (str | Path): Path to the JSON configuration file.
                                           Defaults to "config.json" in the current directory.
        """
        self.config_file_path = Path(config_file_path)
        self.settings = self._load_and_merge_config()

    def _recursive_update(self, base_dict: dict, update_dict: dict) -> None:
        """
        Recursively updates base_dict with values from update_dict.
        """
        for key, value in update_dict.items():
            if isinstance(value, dict) and key in base_dict and isinstance(base_dict[key], dict):
                self._recursive_update(base_dict[key], value)
            else:
                base_dict[key] = value

    def _load_and_merge_config(self) -> dict:
        """
        Loads configuration from the JSON file and merges it with default settings.
        If the config file doesn't exist, it attempts to create one with default values.
        """
        current_settings = DEFAULT_CONFIG.copy() # Start with defaults

        if self.config_file_path.exists() and self.config_file_path.is_file():
            try:
                with open(self.config_file_path, 'r') as f:
                    user_config = json.load(f)
                # Recursively merge user_config into current_settings
                self._recursive_update(current_settings, user_config)
                print(f"INFO: Configuration loaded successfully from: {self.config_file_path}")
            except json.JSONDecodeError as e:
                print(f"ERROR: Failed to decode JSON from {self.config_file_path}: {e}. Using default settings.", file=sys.stderr)
                # current_settings remains DEFAULT_CONFIG
            except Exception as e:
                print(f"ERROR: Could not read config file {self.config_file_path}: {e}. Using default settings.", file=sys.stderr)
                # current_settings remains DEFAULT_CONFIG
        else:
            print(f"WARNING: Config file not found at {self.config_file_path}. Attempting to create with default settings.")
            try:
                self.config_file_path.parent.mkdir(parents=True, exist_ok=True)
                with open(self.config_file_path, 'w') as f:
                    json.dump(DEFAULT_CONFIG, f, indent=4)
                print(f"INFO: Default configuration file created at: {self.config_file_path}")
                # current_settings is already DEFAULT_CONFIG
            except Exception as e:
                print(f"ERROR: Could not create default config file at {self.config_file_path}: {e}. Using in-memory defaults.", file=sys.stderr)
                # current_settings remains DEFAULT_CONFIG

        # Ensure essential paths are created for logging if not present
        try:
            log_path = Path(current_settings.get("log_file_path", DEFAULT_CONFIG["log_file_path"])).expanduser()
            log_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"WARNING: Could not create log directory for {current_settings.get('log_file_path')}: {e}", file=sys.stderr)

        return current_settings

    def get_setting(self, key_path: str, default_value=None):
        """
        Retrieves a setting using a dot-separated key path (e.g., "ssh_keys.include_private_keys").

        Args:
            key_path (str): The dot-separated path to the setting.
            default_value: The value to return if the key is not found.

        Returns:
            The setting value or default_value.
        """
        keys = key_path.split('.')
        value = self.settings
        try:
            for key in keys:
                if isinstance(value, list) and key.isdigit(): # Basic support for list indexing
                    value = value[int(key)]
                else:
                    value = value[key]
            return value
        except (KeyError, TypeError, IndexError):
            return default_value

    # --- Convenience getter methods for common settings ---

    def get_backup_destination(self) -> Path:
        """Returns the fully resolved backup destination path."""
        return Path(self.settings.get("backup_destination_path", DEFAULT_CONFIG["backup_destination_path"])).expanduser()

    def is_encryption_enabled(self) -> bool:
        """Checks if encryption is globally enabled."""
        return bool(self.settings.get("encryption_enabled", DEFAULT_CONFIG["encryption_enabled"]))

    def should_prompt_for_passphrase(self) -> bool:
        """Checks if the utility should prompt for an encryption passphrase."""
        return bool(self.settings.get("encryption_passphrase_prompt", DEFAULT_CONFIG["encryption_passphrase_prompt"]))

    def get_encryption_key_path(self) -> Path | None:
        """Gets the path to a file containing the encryption key/passphrase, if configured."""
        path_str = self.settings.get("encryption_key_path", DEFAULT_CONFIG["encryption_key_path"])
        return Path(path_str).expanduser() if path_str else None

    def get_temporary_staging_path(self) -> Path:
        """Returns the fully resolved temporary staging path for backup operations."""
        return Path(self.settings.get("temporary_staging_path", DEFAULT_CONFIG["temporary_staging_path"])).expanduser()

    def get_archive_format(self) -> str:
        """Returns the desired archive format (e.g., 'tar.gz', 'zip')."""
        return self.settings.get("archive_format", DEFAULT_CONFIG["archive_format"])

    def get_files_to_include_rules(self) -> list:
        """Returns the list of rules defining which files/directories to include in the backup."""
        return self.settings.get("files_to_include", DEFAULT_CONFIG["files_to_include"])

    def get_log_file_path(self) -> Path:
        """Returns the fully resolved path for the log file."""
        return Path(self.settings.get("log_file_path", DEFAULT_CONFIG["log_file_path"])).expanduser()

    def get_log_level(self) -> str:
        """Returns the configured log level (e.g., 'INFO', 'DEBUG')."""
        return self.settings.get("log_level", DEFAULT_CONFIG["log_level"]).upper()

# Example of how to use it (typically done in your main script or manager class)
if __name__ == "__main__":
    # This will look for 'config.json' in the same directory as config.py
    # If not found, it will create one with defaults.
    config = BackupConfig("my_custom_config.json") # You can specify a custom path

    print(f"Backup Destination: {config.get_backup_destination()}")
    print(f"Encryption Enabled: {config.is_encryption_enabled()}")
    print(f"Log Level: {config.get_log_level()}")
    print(f"Log File Path: {config.get_log_file_path()}") # Log dir should have been created if possible

    print("\nFile Inclusion Rules:")
    for rule in config.get_files_to_include_rules():
        print(f"  - Type: {rule.get('type')}, Enabled: {rule.get('enabled')}")
        if rule.get('path'):
            print(f"    Path: {rule.get('path')}")
        if rule.get('patterns'):
            print(f"    Patterns: {rule.get('patterns')}")

    # Example of getting a nested setting
    include_ssh_private_keys = config.get_setting("files_to_include.1.include_private_keys") # Assuming SSH is the second rule
    # A more robust way would be to iterate and find the rule by type:
    ssh_rule = next((r for r in config.get_files_to_include_rules() if r.get("type") == "ssh_keys"), None)
    if ssh_rule:
        include_ssh_private_keys = ssh_rule.get("include_private_keys", False) # Default to False if key missing in rule
    print(f"\nInclude SSH Private Keys (found via iteration): {include_ssh_private_keys}")