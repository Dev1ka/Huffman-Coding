"""
==========================
CANONICAL HUFFMAN DECODING
==========================
"""

current = ""
end = False

with open("Initial-Decoded.txt", "w") as f_out:
    with open('DEFLATE-Compression.txt', 'rb') as f_in:
        # GETTING KEYS
        # Byte 0 - length of header (high + low bytes)
        high_total = f_in.read(1)[0]
        low_total = f_in.read(1)[0]
        total = (high_total << 8) | low_total

        # rebuild char, length dict
        lengths = {}
        for _ in range(total):
            high_byte = f_in.read(1)[0]
            low_byte = f_in.read(1)[0]
            byte_length = f_in.read(1)[0]

            # 16-bit integer token value
            token_val = (high_byte << 8) | low_byte
            # convert integer into char/ 'EOF'
            if token_val == 256:
                token_key = "EOF"

            elif token_val > 255:
                dist = (token_val - 257) >> 5
                length = (token_val - 257) & 0x1F
                token_key = ('pointer', (dist, length))

            else:
                token_key = ('char', chr(token_val))

            lengths[token_key] = byte_length

        # CREATING LOOKUP TABLE
        sorted_dict = sorted(lengths.items(), key=lambda x: (x[1], str(x[0])))
        sorted_chars = [x[0] for x in sorted_dict]
        sorted_lens = [y[1] for y in sorted_dict]

        lookup = {}
        current_code = 0
        prev = 0

        for i in range(len(sorted_chars)):
            char = sorted_chars[i]
            length = sorted_lens[i]

            if prev > 0:
                current_code <<= (length - prev)

            # int val to binary
            bit_string = f"{current_code:0{length}b}"
            lookup[bit_string] = char

            current_code += 1
            prev = length

        # DECODING TEXT
        encoded_data = f_in.read()

        for byte_value in encoded_data:
            if end:
                break

            # byte_value = integer (0-255)
            # bits = string of 8 bits
            bits = f"{byte_value:08b}"
            for bit in bits:
                current += bit

                if current in lookup:
                    token = lookup[current]

                    if token == 'EOF':
                        end = True
                        break

                    token_type = token[0]  # char vs pointer
                    token_val = token[1]

                    if token_type == 'char':
                        f_out.write(token_val)

                    elif token_type == 'pointer':
                        distance, length = token_val
                        f_out.write(f"\0,{distance}_{length},\0")  # convert into original format

                    current = ''

"""
=============
LZ77 DECODING
=============
"""

tuples = []

decoded_text = ""
with open('Initial-Decoded.txt', 'r') as f:
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

with open('DEFLATE-Decoding.txt', 'w') as file:
    file.write(decoded_text)
