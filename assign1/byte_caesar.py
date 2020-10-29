import utils
import string as st
from collections import deque
from itertools import cycle

def encrypt_byte_caesar(filename):

    ciphertext = []

    f = open(filename, "rb")
    
    ba = bytes(f.read())
    for byte in ba:
        ciphertext.append((byte + 3) % 256)

    ba = bytes(ciphertext)
    cipher_image = open("cipherimage.png", "wb")
    cipher_image.write(ba)

    return 'cipherimage.png'

def decrypt_byte_caesar(filename):
    plaintext = []

    f = open(filename, "rb")
    
    ba = bytes(f.read())
    for byte in ba:
        plaintext.append((byte - 3) % 256)

    ba = bytes(plaintext)
    cipher_image = open("goodimage.png", "wb")
    cipher_image.write(ba)

    return filename

decrypt_byte_caesar(encrypt_byte_caesar('black.png'))