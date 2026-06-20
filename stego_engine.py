import cv2
import numpy as np
import os
import zlib
import hashlib
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


def derive_keys(password, salt):
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=64,
        salt=salt,
        iterations=100000,
    )
    key_material = kdf.derive(password.encode())
    return key_material[:32], key_material[32:]


def get_shuffled_indices(total_elements, seed_bytes):
   
    seed_int = int(hashlib.sha256(seed_bytes).hexdigest(), 16) % (2**32)
    rng = np.random.default_rng(seed_int)
    indices = np.arange(total_elements)
    rng.shuffle(indices)
    return indices


def encrypt_message(message, password):
    
    compressed_msg = zlib.compress(message.encode('utf-8'))

    salt = os.urandom(16)
    nonce = os.urandom(12)
    enc_key, _ = derive_keys(password, salt)

    cipher = Cipher(algorithms.AES(enc_key), modes.GCM(nonce))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(compressed_msg) + encryptor.finalize()

    crypto_bundle = salt + nonce + encryptor.tag + ciphertext
    bin_payload = ''.join([format(b, "08b") for b in crypto_bundle])

    magic_header = format(ord('L'), "08b")
    len_header = format(len(bin_payload), "032b")

    return magic_header + len_header + bin_payload


def hide_data_lsb(img, total_payload, password):
    flat_img = img.flatten()
    if len(total_payload) > len(flat_img):
        raise ValueError("Payload size exceeds spatial pixel capacity.")

    shuffle_seed = hashlib.sha256(password.encode()).digest()
    shuffled_indices = get_shuffled_indices(len(flat_img), shuffle_seed)
    target_indices = shuffled_indices[:len(total_payload)]

    bits = np.array([int(bit) for bit in total_payload], dtype=np.uint8)
    flat_img[target_indices] = (flat_img[target_indices] & 254) | bits
    return flat_img.reshape(img.shape)


def hide_data(img_path, total_payload, output_path, password):
    
    img = cv2.imread(img_path)
    if img is None:
        raise FileNotFoundError(f"Image not found at {img_path}")

    out_img = hide_data_lsb(img, total_payload, password)
    cv2.imwrite(output_path, out_img)
    print(f"✅ Secure data injection completed [LSB] -> {output_path}")




def _extract_raw_bits(img, password):
   
   
    shuffle_seed = hashlib.sha256(password.encode()).digest()
    PAYLOAD_START = 40

    flat_img = img.flatten()
    indices = get_shuffled_indices(len(flat_img), shuffle_seed)
    
    def read_bit(idx):
        return str(flat_img[indices[idx]] & 1)

    # Verify Magic Marker Layer
    magic_bits = "".join([read_bit(i) for i in range(8)])
    try:
        if chr(int(magic_bits, 2)) != 'L':
            return "CRITICAL_ERROR: Steganography tracking signature verification failed. Bad password or target file is unindexed."
    except Exception:
        return "CRITICAL_ERROR: Header extraction failure. Verification key invalid."

    payload_len = int("".join([read_bit(i) for i in range(8, 40)]), 2)
    if payload_len <= 0 or (payload_len + PAYLOAD_START) > len(flat_img):
        return "CRITICAL_ERROR: Extracted header limits exceed dimensional frame safety parameters."

    bin_payload = "".join([read_bit(i) for i in range(PAYLOAD_START, PAYLOAD_START + payload_len)])
    return bytes(bytearray([int(bin_payload[i:i + 8], 2) for i in range(0, len(bin_payload), 8)]))


def extract_data(img_path, password):
    
    img = cv2.imread(img_path)
    if img is None:
        raise FileNotFoundError(f"Image not found at {img_path}")
    return _extract_raw_bits(img, password)


def extract_data_from_matrix(img, password):
   
    return _extract_raw_bits(img, password)


def decrypt_message(byte_data, password):
    
    if isinstance(byte_data, str) and "CRITICAL_ERROR" in byte_data:
        return byte_data

    try:
        salt, nonce, tag, ciphertext = byte_data[:16], byte_data[16:28], byte_data[28:44], byte_data[44:]
        enc_key, _ = derive_keys(password, salt)

        cipher = Cipher(algorithms.AES(enc_key), modes.GCM(nonce, tag))
        decryptor = cipher.decryptor()
        compressed_bytes = decryptor.update(ciphertext) + decryptor.finalize()
        return f"🔓 Success: {zlib.decompress(compressed_bytes).decode('utf-8')}"
    except Exception as e:
        return f"❌ Decryption architecture failed (Bad key material or structural truncation): {str(e)}"




if __name__ == "__main__":
    local_pw = "super_secure_password_2026"
    secret_msg = "Classified data packet protected via encryption and signature wrappers."

    if not os.path.exists("cover.png"):
        cv2.imwrite("cover.png", np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8))

    print("--- RUNNING SPATIAL DOMAIN INTERFACE (LSB) ---")
    payload_lsb = encrypt_message(secret_msg, local_pw)
    out_lsb = hide_data_lsb(cv2.imread("cover.png"), payload_lsb, local_pw)
    cv2.imwrite("stego_spatial.png", out_lsb)
    
    extracted_lsb = extract_data("stego_spatial.png", local_pw)
    print(f"Extraction Result -> {decrypt_message(extracted_lsb, local_pw)}\n")