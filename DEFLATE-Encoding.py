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
        file.write(f"{match_dist},{match_len},{next_char}\0")

        cursor += (match_len + 1)

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


# FORMATTING TUPLES
tuples = []

for item in text.split("\0"):
    if not item:
        continue
    dist, length, char = item.split(",", 2)  # only splits first two commas
    tuples.append((int(dist), int(length), char))

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

# ENCODING TEXT
with open("DEFLATE-Compression.txt", "wb") as file:
    code_lookup = dict(zip(chars, codes))

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
