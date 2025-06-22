from Crypto.Cipher import AES
import os

def decrypt_file(input_path, output_path, secret_key):
    # Convert the hex secret key back to bytes
    key = bytes.fromhex(secret_key)
    
    with open(input_path, 'rb') as f_in:
        iv = f_in.read(16)  # Read the IV from the encrypted file
        encrypted_data = f_in.read()  # Read the rest of the encrypted data
    
    cipher = AES.new(key, AES.MODE_CBC, iv)  # AES in CBC mode
    
    # Decrypt the data
    decrypted_data = cipher.decrypt(encrypted_data)
    
    # Remove padding
    pad_length = decrypted_data[-1]
    decrypted_data = decrypted_data[:-pad_length]
    
    with open(output_path, 'wb') as f_out:
        f_out.write(decrypted_data)  # Write the decrypted data
