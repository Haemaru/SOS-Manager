
def num_bin(num, size):
    b = bytearray(size)
    for i in range(size):
        b[i] = (num & (0xff << (i * 8))) >> (i * 8)

    return b
