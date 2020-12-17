"""
Helper functions for creating the GUI menu in the client.
"""

def get_choice(message, options):
    choice = input(message).upper()
    while not choice or choice[0] not in options:
        choice = input("Please enter one of {}. {}".format('/'.join(options), message)).upper()
    return choice[0]

def get_input(message):
    return input(message)