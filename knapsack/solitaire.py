import random
from typing import Callable, List
import functools
import string

class Solitaire:
    """
    Solitaire cipher implementation with a functional approach.
    Most function names are self-explanatory.
    The two jokers have a value of 53 and 54, respectively.
    """
    def __init__(self):
        # Define accepted characters and get their numerical value
        self.letters = string.ascii_letters + string.digits + " .,:!?"
        self.letter_to_num_map = {}

        for i, letter in enumerate(self.letters):
            self.letter_to_num_map[letter] = i

    def encrypt(self, key, msg):
        # Encryption adds the numerical value
        return self.transform(key, msg, lambda n, k: n + k)

    def decrypt(self, key, msg):
        # Decryption decreases the numerical value
        return self.transform(key, msg, lambda n, k: n - k)

    def transform(self, cards, msg, combine):
        to_transform = msg
        cards = list(cards)
        # Compose the transformation steps in reverse order
        run_keystream_sequence = self.compose(self.count_cut,
                                        self.triple_cut_by_jokers,
                                        self.move_joker_b,
                                        self.move_joker_a)
        output = []
        # Loop through message
        while len(output) < len(to_transform):
            # Do the whole Solitaire procedure, get a keystream value
            cards = run_keystream_sequence(cards)
            ks_val = self.get_keystream_value(cards)

            # If we got a joker, do nothing
            if self.is_joker(ks_val, cards):
                continue
            current_letter = to_transform[len(output)]

            # Modify the current letter according to the transform value (encrypt/decrypt it)
            value = combine(self.letter_to_num_map[current_letter], ks_val)
            output.append(self.number_to_letter(value))

        return ''.join(output)

    def generate_cards(self, common_key, suits=4):
        # Randomize a deck based on the common key set up by the clients
        jokers = 2
        deck_size = suits * 13 + jokers
        cards = list(range(1, deck_size + 1))
        random.Random(common_key).shuffle(cards)
        return cards

    def triple_cut_by_jokers(self, cards):
        joker_a = len(cards) - 1
        joker_b = len(cards)
        # Call cutting function with the jokers' positions in the deck
        return self.triple_cut((cards.index(joker_a), cards.index(joker_b)), cards)

    def move_joker_a(self, cards):
        return self.move_joker(len(cards) - 1, cards)

    def move_joker_b(self, cards):
        return self.move_joker(len(cards), cards)

    def get_keystream_value(self, cards):
        index = cards[0] if not self.is_joker(cards[0], cards) else len(cards) - 1
        return cards[index]

    def is_joker(self, value, cards):
        return value > len(cards) - 2

    def move_joker(self, joker, cards):
        # Check if the card would 'jump out' of the deck
        def wraparound(n):
            if n >= len(cards):
                return n % len(cards) + 1
            return n

        cards = list(cards)

        # Depending on which joker we got, move it by 1 or 2 cards down
        jump = 2 if joker is len(cards) else 1
        index = cards.index(joker)
        cards.insert(wraparound(index + jump), cards.pop(index))
        return cards

    def triple_cut(self, cut_indices, cards):
        lower, higher = sorted(cut_indices)
        return cards[higher + 1:] + cards[lower:higher + 1] + cards[:lower]

    def count_cut(self, cards):
        last = len(cards) - 1
        value = cards[last]
        
        # If we got a joker, do nothing.
        if self.is_joker(value, cards):
            return list(cards)

        return cards[value:last] + cards[:value] + [cards[last]]

    def number_to_letter(self, n):
        return self.letters[n % len(self.letters)]

    # One function's result is passed to the next one as input parameter
    # Source: https://mathieularose.com/function-composition-in-python/
    def compose(self, *functions):
        return functools.reduce(lambda f, g: lambda x: f(g(x)), functions)

# Dummy code for testing the functions locally.

# sol = Solitaire()
# input_key = sol.generate_cards("1234")
# print(input_key)
# message = "This is a test string"
# encrypted = sol.encrypt(input_key, message)
# print(encrypted)
# print(sol.decrypt(input_key, encrypted))