"""
=====================
FINDING LONGEST MATCH
=====================
"""


def longest_match(data, cursor, window_size, look_ahead_size):
    """
    Finds longest match within window and look ahead buffer (section to the right of given cursor)
    & returns longest match and dist from cursor to assist in building the LZ77 triple in main loop
    """

    best_dist = 0
    best_len = 0

    # SEARCHING LENGTH OF WINDOW
    for i in range(1, window_size + 1):
        match_index = cursor - i

        if match_index < 0:
            break

        current_len = 0
        while current_len < look_ahead_size and (cursor + current_len) < len(data):
            # FINDING MATCHES OF CHARS IN LOOKAHEAD & WINDOW
            if data[match_index + current_len] == data[cursor + current_len]:
                current_len += 1

            else:
                break

        # SAVING LONGEST MATCH
        if current_len > best_len:
            best_len = current_len
            best_dist = i

    return best_dist, best_len


"""
=====================
ENCODING MATCHES
=====================
"""

with open('example.txt', 'r') as file:
    text = file.read()

with open('LZ77-Compression.txt', 'w') as file:
    window_size = 20
    look_ahead = 10
    cursor = 0

    while cursor < len(text):
        match_dist, match_len = longest_match(text, cursor, window_size, look_ahead)

        # FIND BREAK CHARACTER
        if (cursor + match_len) < len(text):
            next_char = text[cursor + match_len]

        # END OF FILE MARKER
        else:
            next_char = "EOF"

        # WRITE LZ77 TRIPLET INTO FILE
        file.write(f"({match_dist}, {match_len}, {next_char})\n")

        cursor += (match_len + 1)
