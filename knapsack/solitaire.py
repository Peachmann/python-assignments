import random
from typing import Callable, List
import functools
import string

class Solitaire:
    def __init__(self):
        self.letters = string.ascii_letters + string.digits + " ,.?!"
        self.letter_to_num_map = {}

        for i, letter in enumerate(self.letters):
            self.letter_to_num_map[letter] = i

    def encrypt(self, key, msg):
        return self.transform(key, msg, lambda n, k: n + k)

    def decrypt(self, key, msg):
        return self.transform(key, msg, lambda n, k: n - k)

    def transform(self, cards, msg, combine):
        to_transform = msg
        cards = list(cards)
        run_keystream_sequence = self.compose(self.count_cut,
                                        self.triple_cut_by_jokers,
                                        self.move_joker_b,
                                        self.move_joker_a)
        output = []
        while len(output) < len(to_transform):
            cards = run_keystream_sequence(cards)
            ks_val = self.get_keystream_value(cards)
            if self.is_joker(ks_val, cards):
                continue
            current_letter = to_transform[len(output)]
            value = combine(self.letter_to_num_map[current_letter], ks_val)
            output.append(self.number_to_letter(value))

        return ''.join(output)

    def generate_cards(self, common_key, suits=4):
        jokers = 2
        deck_size = suits * 13 + jokers
        cards = list(range(1, deck_size + 1))
        random.Random(common_key).shuffle(cards)
        return cards

    def triple_cut_by_jokers(self, cards):
        joker_a = len(cards) - 1
        joker_b = len(cards)
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
        def wraparound(n):
            if n >= len(cards):
                return n % len(cards) + 1
            return n

        cards = list(cards)
        jump = 2 if joker is len(cards) else 1
        index = cards.index(joker)
        cards.insert(wraparound(index + jump), cards.pop(index))
        return cards

    def triple_cut(self, cut_indices: tuple, cards: list) -> List[int]:
        lower, higher = sorted(cut_indices)
        return cards[higher + 1:] + cards[lower:higher + 1] + cards[:lower]

    def count_cut(self, cards):
        last = len(cards) - 1
        value = cards[last]
        if self.is_joker(value, cards):
            return list(cards)
        return cards[value:last] + cards[:value] + [cards[last]]

    def number_to_letter(self, n):
        return self.letters[n % len(self.letters)]

    def format_input(self, msg):
        return [char for char in msg.upper() if char in self.letter_to_num_map]

    def compose(self, *functions):
        return functools.reduce(lambda f, g: lambda x: f(g(x)), functions)

# sol = Solitaire()
# input_key = sol.generate_cards("1234")
# print(input_key)
# message = "This is a test string"
# encrypted = sol.encrypt(input_key, message)
# print(encrypted)
# print(sol.decrypt(input_key, encrypted))