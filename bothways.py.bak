import os
import shutil
import argparse
import getpass
import pyzipper

class KeyBackupRestore:
    def __init__(self, ssh_key_path, gpg_key_path, password, mode='backup'):
        self.ssh_key_path = ssh_key_path
        self.gpg_key_path = gpg_key_path
        self.password = password
        self.mode = mode
        self.home_dir = os.path.expanduser("~")
        self.temp_dir = os.path.join(self.home_dir, "temp_keys_backup_restore")
        os.makedirs(self.temp_dir, exist_ok=True)

        self.zip_filename = "keys_backup.zip"
        self.zip_path = os.path.join(self.home_dir, self.zip_filename)

    def prepare_files(self):
        # Copy keys into temp directory
        for key_path in [self.ssh_key_path, self.gpg_key_path]:
            if os.path.exists(key_path):
                shutil.copy2(key_path, self.temp_dir)
            else:
                print(f"Warning: {key_path} does not exist.")

    def create_encrypted_zip(self):
        with pyzipper.AESZipFile(self.zip_path, 'w', compression=pyzipper.ZIP_DEFLATED, encryption=pyzipper.WZ_AES) as zf:
            zf.setpassword(self.password.encode())
            for filename in os.listdir(self.temp_dir):
                filepath = os.path.join(self.temp_dir, filename)
                zf.write(filepath, arcname=filename)
        print(f"Backup created at {self.zip_path}")

    def extract_and_restore(self):
        with pyzipper.AESZipFile(self.zip_path, 'r') as zf:
            zf.setpassword(self.password.encode())
            zf.extractall(path=self.temp_dir)
        # Move files back to their original locations or handle as needed
        # For safety, you might ask for confirmation before overwriting existing files
        for filename in os.listdir(self.temp_dir):
            src = os.path.join(self.temp_dir, filename)
            # Determine destination
            dest_path = None
            if filename == os.path.basename(self.ssh_key_path):
                dest_path = self.ssh_key_path
            elif filename == os.path.basename(self.gpg_key_path):
                dest_path = self.gpg_key_path
            # Backup existing files if needed, then restore
            if dest_path:
                shutil.copy2(src, dest_path)
                print(f"Restored {dest_path}")

    def cleanup(self):
        shutil.rmtree(self.temp_dir)

    def run(self):
        if self.mode == 'backup':
            self.prepare_files()
            self.create_encrypted_zip()
            self.cleanup()
        elif self.mode == 'restore':
            if not os.path.exists(self.zip_path):
                print(f"Error: {self.zip_path} does not exist.")
                return
            self.extract_and_restore()
            self.cleanup()


def main():
    parser = argparse.ArgumentParser(description="Backup or restore SSH and GPG keys.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--backup", action='store_true', help="Create backup of keys")
    group.add_argument("--restore", action='store_true', help="Restore keys from backup")
    parser.add_argument("--ssh", type=str, help="Path to your SSH private key")
    parser.add_argument("--gpg", type=str, help="Path to your GPG private key")
    args = parser.parse_args()

    # Prompt for paths if not provided
    ssh_path = args.ssh or input("Enter path to your SSH private key: ")
    gpg_path = args.gpg or input("Enter path to your GPG private key: ")

    # Prompt for password securely
    password = getpass.getpass("Enter encryption password: ")

    mode = 'backup' if args.backup else 'restore'

    backup_restore = KeyBackupRestore(ssh_path, gpg_path, password, mode)
    backup_restore.run()

if __name__ == "__main__":
    main()
