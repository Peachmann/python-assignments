import random
import utils
import numpy

class Merkle_Hellman:
    """
    Merkle-Hellman Knapsack implementation following the specification at
    https://github.com/stanfordpython/python-assignments/tree/master/assign1

    All function names are self-explanatory, steps followed as written.
    """
    def __init__(self, n=8):
        self.n = n
        self.private_key = ''
        self.public_key = ''

    def create_superincreasing_sequence(self):
        sequence = [random.randint(2, 10)]
        total = sequence[0]
        while (len(sequence) < self.n):
            number = random.randint(total + 1, total * 2)
            total += number
            sequence.append(number)

        return tuple(sequence), total

    def generate_private_key(self):
        sequence, total = self.create_superincreasing_sequence()
        q = random.randint(total + 1, total * 2)
        r = random.randint(2, q-1)
        while (not utils.coprime(r, q)):
            r = random.randint(2, q-1)

        return (sequence, q, r)

    # The three parts of the private key are obtained by index
    def generate_public_key(self, private_key):
        return tuple(map(lambda x: private_key[2] * x % private_key[1], private_key[0]))

    def encrypt_mh(self, message, public_key):
        encrypted = []
        for current in message:
            a = utils.byte_to_bits(ord(current))
            c = 0

            for i in range(self.n):
                c += a[i] * public_key[i]

            encrypted.append(c)
        return encrypted

    def decrypt_mh(self, message, private_key):
        w = private_key[0]
        q = private_key[1]
        r = private_key[2]
        s = utils.modinv(r, q)
        decrypted = []
        
        for c in message:
            c_amp = c * s % q
            a = [0] * self.n
            for k in range(self.n - 1, 0, -1):
                if w[k] > c_amp:
                    a[k] = 0
                else:
                    a[k] = 1
                c_amp -= w[k] * a[k]
            decrypted.append(chr(utils.bits_to_byte(tuple(a))))

        return ''.join(decrypted)

# Dummy code for testing the functions locally.

# mh = Merkle_Hellman()
# private_key1 = mh.generate_private_key()
# print(private_key1)
# public_key1 = mh.generate_public_key(private_key1)
# print(public_key1)

# private_key2 = mh.generate_private_key()
# public_key2 = mh.generate_public_key(private_key2)

# encrypted = mh.encrypt_mh("I wonder if this works.", public_key1)
# print(encrypted)
# print(mh.decrypt_mh(encrypted, private_key1))