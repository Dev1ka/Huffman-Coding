import heapq
min_heap = []

# Input: a string of characters
text = "example input"

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
while min_heap:
    node_1 = heapq.heappop(min_heap)[1]
    node_2 = heapq.heappop(min_heap)[1]

    sum = node_1.freq + node_2.freq
    root = Node(None, sum)
    root.left = node_1
    root.right = node_2

    heapq.heappush(min_heap, (sum, root))

print(min_heap)