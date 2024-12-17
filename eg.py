from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

AES_KEY = "226c10029b502d90bc2cdf8a2390a6256c8a799298989089a15c7c0826716ae8"

try:
    KEY = bytes.fromhex(AES_KEY)
except ValueError:
    raise ValueError("Invalid KEY format. It should be a valid hexadecimal string.")
if len(KEY) != 32:
    raise ValueError(f"AES KEY length is invalid. Expected 32 bytes, but got {len(KEY)} bytes.")
if not isinstance(KEY, bytes):
    raise TypeError(f"AES KEY must be of type 'bytes', but got {type(KEY)}.")

def encryption(data: str) -> bytes:
    if data is None:
        raise ValueError("Input is missing.")
    if not isinstance(data, str):
        raise ValueError("Input is not a string type.")
    cipher = AES.new(KEY, AES.MODE_CBC)  
    iv = cipher.iv  
    padded_data = pad(data.encode('utf-8'), AES.block_size)  
    encrypted = cipher.encrypt(padded_data)
    return iv + encrypted  

def decryption(data: bytes) -> str:
    if data is None:
        raise ValueError("Input is missing.")
    if not isinstance(data, bytes):
        raise ValueError("Input is not of 'bytes' type.")
    if len(data) < AES.block_size:
        raise ValueError("Encrypted data is too short to be valid.")
    iv = data[:AES.block_size]  # Extract the IV
    encrypted = data[AES.block_size:]  # Extract the actual encrypted content
    cipher = AES.new(KEY, AES.MODE_CBC, iv)  # Initialize AES cipher with the extracted IV
    decrypted_padded = cipher.decrypt(encrypted)  # Fixed indentation
    try:
        decrypted_data = unpad(decrypted_padded, AES.block_size).decode('utf-8')
    except ValueError:
        raise ValueError("Decryption failed or incorrect padding.")
    return decrypted_data

encrypted_data = encryption("Hello, World!")
print(encrypted_data)
decrypted_data = decryption(encrypted_data)
print(decrypted_data)
