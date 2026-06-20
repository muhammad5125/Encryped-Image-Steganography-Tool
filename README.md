# Encrypted Image Steganography Tool

A web app that hides secret text messages inside images using AES-256-GCM
encryption combined with LSB (Least Significant Bit) steganography. The
password is used both to encrypt the message and to seed a randomized
embedding pattern, so the data is hidden in a non-sequential, key-dependent
way rather than predictable pixel order.

## Features

- AES-256-GCM authenticated encryption with PBKDF2-HMAC-SHA256 key derivation
- Password-seeded shuffled pixel embedding (LSB steganography)
- zlib compression before encryption to maximize usable image capacity
- Magic-byte header for verifying correct password / image integrity before decryption
- Streamlit web interface with separate encrypt and decrypt workflows
- Live console log of each cryptographic step

## Tech Stack

Python · OpenCV · Streamlit · Cryptography (AES-256-GCM) · NumPy

## How to Run

```bash
pip install opencv-python streamlit cryptography numpy
streamlit run app.py
```

## Files

- `stego_engine.py` — core encryption, compression, and LSB embedding/extraction logic
- `app.py` — Streamlit web interface
