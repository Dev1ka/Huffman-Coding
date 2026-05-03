# Input: a string of characters
text = "example input"

# Creating frequency table
freq = {}

for char in text:
    freq[char] = freq.get(char, 0) + 1
