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

with open('LZ77-Compression.txt', 'w') as file:
    window_size = 0
    cursor = 0
    look_ahead = 0
    data = ''

    while cursor <= len(data):
        match_dist, match_len = longest_match(data)
        '''
        FUNCTION:
        - Call the function to find the longest match between the search buffer
          and the look-ahead buffer
        - Store the result as an LZ77 triplet (distance to match, length of match, next character)
        - Move the cursor forward plus the next character
        '''
        pass
