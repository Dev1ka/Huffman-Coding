current = ""
end = False

with open("decoded.txt", "w") as f_out:
    with open('compressed.txt', 'rb') as f_in:
        # GETTING KEYS
        chars = f_in.readline().decode('utf-8').strip().split(',')
        codes = f_in.readline().decode('utf-8').strip().split(',')

        f_in.readline()
        lookup = dict(zip(codes, chars))

        # DECODING TEXT
        encoded_data = f_in.read()

        for byte_value in encoded_data:
            if end:
                break

            # byte_value = integer (0-255)
            # bits = string of 8 bits
            bits = f"{byte_value:08b}"
            for bit in bits:
                current += bit
                if current in lookup:
                    if lookup[current] == 'EOF':
                        end = True
                        break

                    f_out.write(lookup[current])
                    current = ''
