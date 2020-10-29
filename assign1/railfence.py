import error_handling as er

#################
# RAILFENCE CIPHER #
#################

def encrypt_railfence(plaintext, num_rails):
    if not er.verify_input(plaintext):
        return "Incorrect input"

    ciphertext, matrix = "", [["" for x in range(len(plaintext))] for y in range(num_rails)]
    increment = 1
    row = 0
    col = 0
    n = len(matrix)

    for c in plaintext:
        if row + increment < 0 or row + increment >= n:
            increment = increment * -1

        matrix[row][col] = c
        row += increment
        col += 1

    for list in matrix:
        ciphertext += "".join(list)

    return ciphertext


def decrypt_railfence(cipthertext, num_rails):
    if not er.verify_input(cipthertext):
        return "Incorrect input"

    plaintext, matrix = "", [["" for x in range(len(cipthertext))] for y in range(num_rails)]

    idx = 0
    increment = 1
    row_length = len(cipthertext)

    for selected_row in range(0, num_rails):
        row = 0
        for col in range(0, row_length):
            if row + increment < 0 or row + increment >= num_rails:
                increment *= -1
            
            if row == selected_row:
                matrix[row][col] += cipthertext[idx]
                idx += 1
            
            row += increment

    # Transpose matrix to get the text (every column has 1 letter only)
    for list in zip(*matrix):
        plaintext += "".join(list)

    return plaintext

print(decrypt_railfence(encrypt_railfence("WEAREDISCOVEREDFLEEATONCE", 6), 6))