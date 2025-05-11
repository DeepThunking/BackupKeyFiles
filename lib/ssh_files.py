"""
Identifies and lists potential SSH-related file paths in the user's
home directory for backup purposes.

This script compiles a list of common SSH key files (standard and some
deprecated types), the SSH client configuration file (`config`),
`known_hosts`, and `authorized_keys`. The result is a sorted list of
`pathlib.Path` objects, each pointing to a potential SSH file.
"""

from pathlib import Path

def get_potential_ssh_file_paths(ssh_dir: Path) -> list[Path]:
    """
    Generates a list of potential SSH-related file paths within a given SSH directory.

    The list includes common private/public key pairs, the 'config' file,
    'known_hosts', 'authorized_keys', and some deprecated key file names.

    Args:
        ssh_dir: A pathlib.Path object representing the .ssh directory
                 (e.g., Path.home() / '.ssh').

    Returns:
        A sorted list of pathlib.Path objects, where each object is a full
        path to a potential SSH file.
    """
    # Define base names for standard keys
    standard_key_basenames = [
        'id_rsa',
        'id_ecdsa',
        'id_ed25519',
        'id_ecdsa_sk',
        'id_ed25519_sk'
    ]

    # Define names for other specific files, including deprecated ones
    # and essential files like config, known_hosts.
    other_ssh_filenames = [
        'config',          # SSH client configuration
        'known_hosts',     # List of known host keys
        'authorized_keys', # Public keys authorized to log into this machine
        'id_dsa',          # Deprecated DSA private key
        'id_dsa.pub',      # Deprecated DSA public key
        'identity', #Deprecated
        'identity.pub' #Deprecated
    ]

    # Use a set to store all potential full Path objects to ensure uniqueness
    # before converting to a sorted list.
    potential_paths_set = set()

    # Add the config file and other specific files
    for filename in other_ssh_filenames:
        potential_paths_set.add(ssh_dir / filename)

    # Add standard private and public keys
    for basename in standard_key_basenames:
        potential_paths_set.add(ssh_dir / basename)         # Private key file
        potential_paths_set.add(ssh_dir / (basename + ".pub")) # Corresponding public key file

    # Convert the set to a sorted list for consistent order and return
    return sorted(list(potential_paths_set))

# --- Main execution block (example usage) ---
if __name__ == "__main__":
    home_directory = Path.home()
    dot_ssh_directory = home_directory / '.ssh'
    # Get the list of potential SSH files using the function
    possible_ssh_files = get_potential_ssh_file_paths(dot_ssh_directory)

    print("List of potential SSH files to consider for backup:")
    for file_path in possible_ssh_files:
        print(file_path)

actual_files_to_backup = [p for p in possible_ssh_files if p.is_file()]
print("\nActual SSH files found (and are files):")
for f in actual_files_to_backup:
    print(f)