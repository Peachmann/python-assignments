from unittest import TestCase
from knapsack import Merkle_Hellman
from solitaire import Solitaire
import solitaire


class KnapSackTest(TestCase):
    def test_encrypt(self):
        message = "This is a test string"
        public_key = (295, 592, 301, 14, 28, 353, 120, 236)
        answer = [959, 921, 1157, 1263, 301, 1157, 1263, 301, 1129, 301,
                  1260, 1482, 1263, 1260, 301, 1263, 1260, 1027, 1157, 1394, 1602]
        self.assertEqual(
            answer, Merkle_Hellman().encrypt_mh(message, public_key))

    def test_decrypt(self):
        message = [959, 921, 1157, 1263, 301, 1157, 1263, 301, 1129, 301,
                   1260, 1482, 1263, 1260, 301, 1263, 1260, 1027, 1157, 1394, 1602]
        private_key = ((2, 7, 11, 21, 42, 89, 180, 354), 881, 588)
        answer = "This is a test string"
        self.assertEqual(
            answer, Merkle_Hellman().decrypt_mh(message, private_key))


class SolitaireTest(TestCase):
    def test_encrypt(self):
        message = "This is a test string"
        cards = [7, 33, 15, 41, 19, 14, 5, 28, 53, 20, 39, 23, 44, 8, 54, 2, 22, 37, 24, 3, 31, 25, 50, 45, 47, 51,
                18, 49, 43, 6, 36, 21, 4, 52, 26, 34, 35, 30, 13, 10, 12, 11, 38, 9, 27, 32, 1, 29, 46, 40, 17, 42, 48, 16]
        answer = "73uuRD CQJBPXxGM943sI"
        self.assertEqual(answer, Solitaire().encrypt(cards, message))

    def test_decrypt(self):
        message = "73uuRD CQJBPXxGM943sI"
        cards = [7, 33, 15, 41, 19, 14, 5, 28, 53, 20, 39, 23, 44, 8, 54, 2, 22, 37, 24, 3, 31, 25, 50, 45, 47, 51,
                18, 49, 43, 6, 36, 21, 4, 52, 26, 34, 35, 30, 13, 10, 12, 11, 38, 9, 27, 32, 1, 29, 46, 40, 17, 42, 48, 16]
        answer = "This is a test string"
        self.assertEqual(answer, Solitaire().decrypt(cards, message))
