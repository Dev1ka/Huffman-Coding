def longest_match(data, cursor, window_size, look_ahead_size):
    best_dist = 0
    best_len = 0

    '''
    FUNCTION:
    Loop through the search buffer to find the longest match with the look-ahead buffer,
    return match length and distance from cursor to all instances of pattern
    '''

    return best_dist, best_len


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
