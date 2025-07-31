import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from pathlib import Path

# Decrypt secret values
fernet_key = os.getenv('FERNET_KEY')
fernet = Fernet(fernet_key.encode())

def decrypt_env_var(enc_value: str) -> str:
    return fernet.decrypt(enc_value.encode()).decode()

def encrypt_value(value: str) -> str:
    return fernet.encrypt(value.encode()).decode()
