# IMPORTS
import heapq
import sys
import getopt
import time
import os

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
min_heap = []

with open(input_file, 'r') as file:
    text = file.read()

original_size = os.path.getsize(input_file)
start_time = time.time()

"""
=======================
ASSIGNING INITIAL CODES
=======================
"""


# BINARY TREE TRAVERSAL FUNCTION
def assign_codes(node, current_code, codes):
    if node.left is None and node.right is None:
        codes[node.char] = current_code
        return

    if node.left:
        assign_codes(node.left, current_code + "0", codes)

    if node.right:
        assign_codes(node.right, current_code + "1", codes)


# BINARY TREE CLASS
class Node:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq


def build_huffman_tree(text):
    # CREATING FREQUENCY TABLE
    freq = {}

    for char in text:
        freq[char] = freq.get(char, 0) + 1

    for key, val in freq.items():
        heapq.heappush(min_heap, (val, Node(key, val)))
    heapq.heappush(min_heap, (1, Node('EOF', 1)))

    # CONSTRUCTING BINARY TREE
    while len(min_heap) != 1:
        node_1 = heapq.heappop(min_heap)[1]
        node_2 = heapq.heappop(min_heap)[1]

        sum = node_1.freq + node_2.freq
        root = Node(None, sum)
        root.left = node_1
        root.right = node_2

        heapq.heappush(min_heap, (sum, root))

    # ASSIGNING BINARY CODES
    code = {}
    lengths = {}
    root = heapq.heappop(min_heap)[1]

    assign_codes(root, '', code)

    for key, val in code.items():
        lengths[key] = len(val)

    return lengths


def get_canonical_codes(lengths):
    # FINDING CANONICAL HUFFMAN CODES
    sorted_dict = sorted(lengths.items(), key=lambda x: (x[1], x[0]))
    sorted_chars = [x[0] for x in sorted_dict]
    sorted_lens = [y[1] for y in sorted_dict]

    codes = []
    chars = []
    current_code = 0
    prev = 0

    for i in range(len(sorted_chars)):
        char = sorted_chars[i]
        length = sorted_lens[i]

        if prev > 0:
            current_code <<= (length - prev)

        chars.append(char)
        codes.append(f"{current_code:0{length}b}")

        current_code += 1
        prev = length

    return dict(zip(chars, codes))


def write_compressed(output_file, text, code_lookup):
    with open(output_file, "wb") as file:
        # WRITING DECODING INFO
        header = bytearray()

        # byte 0 (total number of chars)
        header.append(len(code_lookup))

        # ASCII val, bit-length
        for char, code in code_lookup.items():
            # find integer val of token
            if char == 'EOF':
                token_val = 256
            else:
                token_val = ord(char)  # convert character to its 0-255 integer value

            # split the 16-bit integer into two 8-bit bytes
            high_byte = (token_val >> 8) & 0xFF  # 00000001 for EOF, 00000000 for everything else
            low_byte = token_val & 0xFF

            # write into header arr
            header.append(high_byte)
            header.append(low_byte)
            header.append(len(code))  # stores bit-length as a single byte

        file.write(header)

        # ENCODING REST OF FILE
        buffer = 0
        count = 0

        for i in text:
            current = code_lookup[i]
            for x in current:
                buffer <<= 1
                buffer |= int(x)
                count += 1

                if count == 8:
                    file.write(bytes([buffer]))
                    buffer = 0
                    count = 0

        # HANDLING OVERFLOW
        end_code = code_lookup['EOF']
        for y in end_code:
            buffer <<= 1
            buffer |= int(y)
            count += 1

            if count == 8:
                file.write(bytes([buffer]))
                buffer = 0
                count = 0
        if count != 0:
            while count < 8:
                buffer <<= 1
                buffer |= 0
                count += 1
            file.write(bytes([buffer]))


lengths = build_huffman_tree(text)
code_lookup = get_canonical_codes(lengths)
write_compressed(output_file, text, code_lookup)

end_time = time.time()
compressed_size = os.path.getsize(output_file)
compression_ratio = (1 - compressed_size / original_size) * 100

print(f"Total time:     {end_time - start_time:.3f}s")
print(f"Original size:  {original_size} bytes")
print(f"Compressed size:{compressed_size} bytes")
print(f"Compression:    {compression_ratio:.1f}%")