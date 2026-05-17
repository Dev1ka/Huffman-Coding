# IMPORTS
import heapq
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
=============
LZ77 ENCODING
=============
"""

# SET CONSTANT VARIABLES
window_size = 4096
look_ahead = 258
emit_match = 8
min_match = 3
max_chain = 246 # maximum matches checked per loop


def _hash3(data, position):
    """
    Converts 3 consecutive characters into a single integer to use as a key instead of re-searching
    every character in window every loop
    """
    return (ord(data[position]) << 16) | (ord(data[position + 1]) << 8) | ord(data[position + 2])


def _update_hash(data, position, location, prev):
    """
    Saves location of 3 char key for future use
    """
    if position + 2 < len(data):
        h = _hash3(data, position)  # gets hash of data[position] and the two characters after it as 1 int
        prev[position] = location[h]  # change current position to previous occurrence
        location[h] = position  # update most recent occurrence


def lz77_encode(data, output_file):
    num = len(data)
    cursor = 0
    locations = {}
    prev = [0] * num

    with open(output_file, 'w') as file:
        while cursor < num:
            # RESET PATTERN INFO
            best_dist = 0
            best_len = 0

            if cursor + min_match <= num:  # only search if enough chars
                h = _hash3(data, cursor)  # encode next three chars
                chain = locations[h]  # lookup prev occurrences (shorten manual search)
                checked = 0

                while chain and checked < max_chain:  # go through each occurrence
                    dist = cursor - chain  # distance to match
                    if dist > window_size:  # stop if dist exceeds window limit
                        break

                    limit = min(look_ahead, num - cursor)
                    match_length = 0
                    while match_length < limit and data[chain + match_length] == data[cursor + match_length]:
                        match_length += 1  # manual search until limit reached

                    if match_length > best_len:  # save the longest match
                        best_len = match_length
                        best_dist = dist

                    chain = prev[chain]
                    checked += 1

            if best_len >= emit_match:  # saving pointer
                file.write(f"\0,{best_dist}_{best_len},\0")
                end = cursor + best_len
                for i in range(cursor, min(end, num - 2)):
                    _update_hash(data, i, locations, prev)
                cursor = end

            else:  # saving individual char
                file.write(data[cursor])
                _update_hash(data, cursor, locations, prev)
                cursor += 1


# CONVERTING LZ77 OUTPUT INTO TUPLES
with open(output_file, 'r') as f:
    content = f.read()

tuples = []
cursor = 0

while cursor < len(content):
    if content[cursor] == '\0':
        end_marker = content.find('\0', cursor + 1)
        marker_inside = content[cursor + 1: end_marker].strip(',')

        dist_str, len_str = marker_inside.split('_')
        dist = int(dist_str)
        match_len = int(len_str)

        tuples.append(('pointer', (dist, match_len)))  # adding tokens separately
        cursor = end_marker + 1
    else:
        tuples.append(('char', content[cursor])) # adding individual characters separately
        cursor += 1

"""
==========================
CANONICAL HUFFMAN ENCODING
==========================
"""

min_heap = []

with open(output_file, 'r') as file:
    text = file.read()


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
        if self.freq != other.freq:
            return self.freq < other.freq
        return str(self.char) < str(other.char)


# CREATING FREQUENCY TABLE
freq = {}

for x in tuples:
    freq[x] = freq.get(x, 0) + 1

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

# FINDING CANONICAL HUFFMAN CODES
sorted_dict = sorted(lengths.items(), key=lambda x: (x[1], str(x[0])))
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

# ENCODING TEXT (HEADER)
with open(output_file, "wb") as file:
    code_lookup = dict(zip(chars, codes))

    # WRITING DECODING INFO
    header = bytearray()

    # BYTE 0 (total number of chars)
    total = len(code_lookup)
    header.append((total >> 8) & 0xFF)
    header.append(total & 0xFF)

    # MAPPING SPECIAL TOKENS TO IDs FOR ENCODING
    pointer_id = 257
    pointer_map = {}

    for token, code in code_lookup.items():
        if token == 'EOF':  # EOF special encoding
            token_val = 256

        elif type(token) == tuple and token[0] == 'char':
            token_val = ord(token[1])  # single char

        elif type(token) == tuple and token[0] == 'pointer':
            distance, length = token[1]
            # special character starting point to differentiate pointers
            header.append(0xFF)
            header.append(0xFE)

            header.append((distance >> 8) & 0xFF)  # high byte
            header.append(distance & 0xFF)  # low byte
            header.append((length >> 8) & 0xFF)  # high byte
            header.append(length & 0xFF)  # low byte
            header.append(len(code))
            continue

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

    for i in tuples:
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
