# encryptor.py
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import os
import hashlib

class FileEncryptor:
    def __init__(self, passphrase: str):
        # Derive a key from the passphrase (use a proper KDF like scrypt or Argon2 in a real app)
        # For simplicity here, we'll use SHA256, but this is NOT recommended for password hashing directly for key derivation.
        # Use PBKDF2HMAC or a more robust KDF.
        self.key = hashlib.sha256(passphrase.encode()).digest() # 32 bytes for AES-256
        self.aesgcm = AESGCM(self.key)

    def encrypt_file(self, input_file_path: Path, output_file_path: Path):
        nonce = os.urandom(12)  # GCM nonce, 96 bits is recommended
        with open(input_file_path, 'rb') as f_in, open(output_file_path, 'wb') as f_out:
            f_out.write(nonce) # Store nonce with ciphertext
            plaintext = f_in.read()
            ciphertext = self.aesgcm.encrypt(nonce, plaintext, None) # No associated data
            f_out.write(ciphertext)
        print(f"Encrypted: {input_file_path} -> {output_file_path}")

    def decrypt_file(self, input_file_path: Path, output_file_path: Path):
        with open(input_file_path, 'rb') as f_in, open(output_file_path, 'wb') as f_out:
            nonce = f_in.read(12) # Read the nonce
            ciphertext = f_in.read()
            plaintext = self.aesgcm.decrypt(nonce, ciphertext, None)
            f_out.write(plaintext)
        print(f"Decrypted: {input_file_path} -> {output_file_path}")