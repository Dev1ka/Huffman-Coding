import heapq

"""
=============
LZ77 ENCODING
=============
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


with open('example.txt', 'r') as file:
    text = file.read()

with open('Initial-Compression.txt', 'w') as file:
    window_size = 4096
    look_ahead = 258
    cursor = 0

    while cursor < len(text):
        match_dist, match_len = longest_match(text, cursor, window_size, look_ahead)

        # WRITE MATCHES LONG ENOUGH TO OUTWEIGH 7 BYTE TOKEN COST
        if match_len >= 8:
            file.write(f"\0,{match_dist}_{match_len},\0")
            cursor += match_len

        else:
            current_char = text[cursor]
            file.write(current_char)
            cursor += 1

# CONVERTING LZ77 OUTPUT INTO TUPLES
with open('Initial-Compression.txt', 'r') as f:
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

with open('Initial-Compression.txt', 'r') as file:
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
with open("DEFLATE-Compression.txt", "wb") as file:
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
