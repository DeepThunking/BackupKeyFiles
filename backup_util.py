# backup_util.py
import argparse
from lib.manager import BackupManager
from lib.config import BackupConfig
from lib.archiver import Archiver
from lib.discoverer import FileDiscoverer
from lib.encryptor import FileEncryptor

def main():
    parser = argparse.ArgumentParser(description="Backup and encryption utility.")
    parser.add_argument("action", choices=["backup", "restore"], help="Action to perform.")
    parser.add_argument("--config", default="config.json", help="Path to configuration file.")
    # Future: Add arguments for: --backup-file, --restore-to
    
    args = parser.parse_args()
    backup_config = BackupConfig(args.config)
    manager = BackupManager(backup_config)

    if args.action == "backup":
    
        try:
            manager = BackupManager(config_path=args.config) 
            manager.run_backup()
        except Exception as e:
            print(f"An error occurred: {e}")
            import traceback
            traceback.print_exc()

    elif args.action == "restore":
        print("Restore functionality not implemented.")
        # manager.restore_backup(args.backup_file, args.restore_to)

if __name__ == "__main__":
#    Self.discoverer = FileDiscoverer(config=Self) # manager passes itself to act as config provider
    main()