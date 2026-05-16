tuples = []

"""
=================================
PARSING MIXED LZ77 TEXT + MARKERS
=================================
"""

decoded_text = ""
with open('LZ77-Compression.txt', 'r') as f:
    content = f.read()

cursor = 0
while cursor < len(content):
    if content[cursor] == '\0':  # start of token
        end_marker = content.find('\0', cursor + 1)  # start at cursor + 1, end at end of token

        # SAVE CONTENTS
        marker_inside = content[cursor + 1: end_marker]

        # STRIP FORMATTING
        marker_inside = marker_inside.strip(',')
        dist_str, len_str = marker_inside.split('_')
        dist = int(dist_str)
        match_len = int(len_str)

        # DECODE THE POINTER
        start_index = len(decoded_text) - dist
        for i in range(match_len):
            decoded_text += decoded_text[start_index + i]

        cursor = end_marker + 1

    else:
        decoded_text += content[cursor]  # uncompressed chars
        cursor += 1

"""
=============
WRITING FILE
=============
"""

with open('LZ77-Decoded.txt', 'w') as file:
    file.write(decoded_text)
