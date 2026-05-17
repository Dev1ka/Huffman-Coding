# IMPORTS
import sys
import getopt

# CLI
program_name = sys.argv[0]

# Initialize variables
input_file = None
output_file = None

try:
    # Parse arguments excluding the program name
    opts, args = getopt.getopt(sys.argv[1:], "hi:o:", ["help", "input=", "output="])
except getopt.GetoptError as err:
    print(f"Error: {err}")
    print(f"Usage: {program_name} -i <input_file> -o <output_file>")
    sys.exit()

for opt, arg in opts:
    if opt in ("-h", "--help"):
        print(f"Usage: {program_name} -i <input_file> -o <output_file>")
        sys.exit()
    elif opt in ("-i", "--input"):
        input_file = arg
    elif opt in ("-o", "--output"):
        output_file = arg

if input_file is None or output_file is None:
    print(f"Usage: {program_name} -i <input_file> -o <output_file>")
    sys.exit()

"""
==========================
CANONICAL HUFFMAN DECODING
==========================
"""


def build_lookup_table(f_in):
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

        token_val = (high_byte << 8) | low_byte
        if token_val == 256:
            byte_length = f_in.read(1)[0]
            token_key = "EOF"

        elif high_byte == 0xFF and low_byte == 0xFE:
            # (distance)
            dist_hi = f_in.read(1)[0]  # high byte
            dist_lo = f_in.read(1)[0]  # low byte
            # (length)
            len_hi = f_in.read(1)[0]  # high byte
            len_lo = f_in.read(1)[0]  # low byte
            byte_length = f_in.read(1)[0]
            token_key = ('pointer', ((dist_hi << 8) | dist_lo, (len_hi << 8) | len_lo))  # append full 16 bit val

        else:
            byte_length = f_in.read(1)[0]
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

    return lookup


def huffman_decode(input_file, output_file):
    current = ""
    end = False

    with open(output_file, "w") as f_out:
        with open(input_file, 'rb') as f_in:
            lookup = build_lookup_table(f_in)

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


def lz77_decode(output_file):
    decoded_text = ""

    with open(output_file, 'r') as f:
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

    with open(output_file, 'w') as file:
        file.write(decoded_text)


huffman_decode(input_file, output_file)
lz77_decode(output_file)