# encrypt_file.py
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import os

def encrypt_file(input_path, output_path):
    # Generate a random 32-byte secret key
    secret_key = get_random_bytes(32)  # 32 bytes = 256-bit key
    iv = get_random_bytes(16)  # Generate a random 16-byte IV for AES

    cipher = AES.new(secret_key, AES.MODE_CBC, iv)  # AES in CBC mode

    with open(input_path, 'rb') as f_in:
        file_data = f_in.read()

    # Pad data to make its length a multiple of AES block size (16 bytes)
    pad_length = 16 - len(file_data) % 16
    file_data += bytes([pad_length]) * pad_length

    encrypted_data = cipher.encrypt(file_data)

    with open(output_path, 'wb') as f_out:
        f_out.write(iv)  # Write the IV to the beginning of the file
        f_out.write(encrypted_data)  # Write the encrypted data

    # Return the secret key (you might want to store this or handle it in a secure way)
    return secret_key.hex()  # This can be logged or handled in your application
