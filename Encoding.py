import heapq
min_heap = []

# Input: a string of characters
text = "example input"

# Creating binary tree
class Node:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

# Creating frequency table
freq = {}

for char in text:
    freq[char] = freq.get(char, 0) + 1

for key, val in freq.items():
    heapq.heappush(min_heap, (val, Node(key, val)))