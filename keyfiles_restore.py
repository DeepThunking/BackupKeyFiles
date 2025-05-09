import pyzipper

def restore_keys(zip_path, password, extract_to):
    with pyzipper.AESZipFile(zip_path, 'r') as zf:
        zf.setpassword(password.encode())
        zf.extractall(path=extract_to)

# Example:
# restore_keys('/path/to/keys_backup.zip', 'your_password', '/desired/extract/path')
