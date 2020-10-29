import math
import error_handling as er
#################
# SCYTALE CIPHER #
#################

def encrypt_scytale(plaintext, circumference):
    """Encrypt a plaintext using a Scytale cipher.

    :param plaintext: The message to encrypt.
    :type plaintext: str
    :param circumference: The circumference of the rod.
    :type circumference: int

    :returns: The encrypted ciphertext.
    """

    if not er.verify_input(plaintext):
        return "Incorrect input"

    ciphertext = ''
    text_length = len(plaintext)
    starting_point = 0

    if text_length < circumference:
        return plaintext

    while len(plaintext) % circumference != 0:
	    plaintext += '~'

    text_length = len(plaintext)

    while starting_point < circumference:
        # Get i-th char, make it a string list and join them
        ciphertext += ''.join(map(str, list((plaintext[i] for i in range(starting_point, text_length, circumference)))))
        starting_point += 1

    return ciphertext

def decrypt_scytale(ciphertext, circumference):
    """Decrypt a plaintext using a Scytale cipher.

    :param plaintext: The message to decrypt.
    :type plaintext: str
    :param circumference: The circumference of the rod.
    :type circumference: int

    :returns: The decrypted plaintext.
    """

    plaintext = ''
    text_length = len(ciphertext)
    starting_point = 0

    if text_length < circumference:
        return ciphertext

    circumference = math.ceil((text_length / circumference))
    
    while starting_point < circumference:
        plaintext += ''.join(map(str, list((ciphertext[i] for i in range(starting_point, text_length, circumference)))))
        starting_point += 1

    return plaintext

print(decrypt_scytale(encrypt_scytale("HELOSZIAA", 3), 3))