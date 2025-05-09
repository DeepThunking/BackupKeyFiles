import os
import pyzipper
import shutil

class KeyBackup:
    def __init__(self, ssh_key_path, gpg_key_path, zip_password, zip_filename="keys_backup.zip"):
        self.ssh_key_path = ssh_key_path
        self.gpg_key_path = gpg_key_path
        self.zip_password = zip_password
        self.zip_filename = zip_filename
        self.home_dir = os.path.expanduser("~")
        self.temp_dir = os.path.join(self.home_dir, "temp_keys_backup")
        os.makedirs(self.temp_dir, exist_ok=True)

    def prepare_files(self):
        # Copy the key files into a temporary directory
        for key_path in [self.ssh_key_path, self.gpg_key_path]:
            if os.path.exists(key_path):
                shutil.copy2(key_path, self.temp_dir)
            else:
                print(f"Warning: {key_path} does not exist.")
    
    def create_encrypted_zip(self):
        zip_path = os.path.join(self.home_dir, self.zip_filename)
        with pyzipper.AESZipFile(zip_path,
                                 'w',
                                 compression=pyzipper.ZIP_DEFLATED,
                                 encryption=pyzipper.WZ_AES) as zf:
            zf.setpassword(self.zip_password.encode())
            for filename in os.listdir(self.temp_dir):
                filepath = os.path.join(self.temp_dir, filename)
                zf.write(filepath, arcname=filename)
        return zip_path

    def cleanup(self):
        # Remove the temporary directory and files
        shutil.rmtree(self.temp_dir)

    def run_backup(self):
        self.prepare_files()
        zip_path = self.create_encrypted_zip()
        self.cleanup()
        print(f"Backup created at {zip_path}")

# Usage example:
# Replace these with your actual key paths and a strong password
if __name__ == "__main__":
    ssh_key = "/path/to/your/id_rsa"
    gpg_key = "/path/to/your/gpg_private.key"
    password = "your_strong_password"  # Use a secure password

    backup = KeyBackup(ssh_key, gpg_key, password)
    backup.run_backup()
