from compression import zstd
import main


data = b"abcdefghijklmnopqrstuvwxyz" * 20
compressed = zstd.compress(data)
ratio = len(compressed) / len(data)
print(f"Compressed from {len(data)} to {len(compressed)} bytes ({ratio:.0%})\n")

print(compressed)