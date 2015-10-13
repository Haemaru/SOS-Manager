
def num_bin(num, size):

    b = bytearray(size)
    for i in range(size):
        b[i] = (num & (0xff << (i * 8))) >> (i * 8)

    return b


def bin_num(binary, size):

    n = 0
    for i in range(size):
        n += binary[i] << (i * 8)

    return n


def is_bit_flagged(data, flag_bit):
    return (data & flag_bit) != flag_bit
