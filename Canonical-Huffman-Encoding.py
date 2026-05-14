# INITIALISING MINHEAP
import heapq
min_heap = []

with open('example.txt', 'r') as file:
    text = file.read()

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

"""
=========================
ASSIGNING CANONICAL CODES
=========================
"""

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

"""
========================
CREATING COMPRESSED FILE
========================
"""

with open("compressed.txt", "wb") as file:
    # WRITING ARRAYS AS METADATA
    chars_line = ",".join(chars) + "\n"
    codes_line = ",".join(codes) + "\n"

    file.write(chars_line.encode('utf-8'))
    file.write(codes_line.encode('utf-8'))

    file.write(b"\n")

    # ENCODING REST OF FILE
    code_lookup = dict(zip(chars, codes))
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
    end_code = code['EOF']
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
