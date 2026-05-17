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

# MAIN
current = ""
end = False


def build_lookup_table(f_in):
    # GETTING KEYS
    byte_0 = f_in.read(1)  # byte 0 - length of header
    total = byte_0[0]

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
        else:
            token_key = chr(token_val)

        lengths[token_key] = byte_length

    # CREATING LOOKUP TABLE
    sorted_dict = sorted(lengths.items(), key=lambda x: (x[1], x[0]))
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
                        if lookup[current] == 'EOF':
                            end = True
                            break

                        f_out.write(lookup[current])
                        current = ''


huffman_decode(input_file, output_file)
