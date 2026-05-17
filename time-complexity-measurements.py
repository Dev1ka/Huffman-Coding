with open("bee-movie-script.txt", "r", encoding="utf-8") as f:
    bee_script = f.read()

# Generate your scaling files
sizes_in_kb = [25, 50, 100, 200, 400, 800]

for size in sizes_in_kb:
    target_bytes = size * 1024
    # Repeat the script until it hits the target size
    final_text = (bee_script * (target_bytes // len(bee_script) + 1))[:target_bytes]

    with open(f"bee_{size}kb.txt", "w", encoding="utf-8") as f_out:
        f_out.write(final_text)