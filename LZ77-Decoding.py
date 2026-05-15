tuples = []

with open('LZ77-Compression.txt', 'r') as f:
    content = f.read()
    for item in content.split(")"):
        if not item:
            continue

        item = item.strip("(")
        dist, length, char = item.split(",") # 4 COMMA ISSUE
        tuples.append((int(dist), int(length), char))

decoded_text = ""
for dist, length, next_char in tuples:
    if length > 0:
        start_index = len(decoded_text) - dist
        for i in range(length):
            decoded_text += decoded_text[start_index + i]

    if next_char:
        decoded_text += next_char

with open('LZ77-Decoded.txt', 'w') as file:
    file.write(decoded_text)
