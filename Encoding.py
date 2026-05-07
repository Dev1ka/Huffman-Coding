import heapq
min_heap = []

"""
================
FORMATTING INPUT
================    
"""
# Input: a string of characters
text = "example input"

"""
===============
ASSIGNING CODES
===============
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
root = heapq.heappop(min_heap)[1]

assign_codes(root, '', code)
print(code)

"""
========================
CREATING COMPRESSED FILE
========================
"""

compressed_code = ''

for i in text:
    compressed_code += code[i]