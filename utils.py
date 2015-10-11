
def num_bin(num, size):
    b = bytearray(size)
    for i in range(size):
        b[i] = (num & (0xff << (i * 8))) >> (i * 8)

    return b


def bin_num(binary, size):
    ret = 0
    for i in range(size):
        print(binary[i])
        ret |= ord(binary[i]) << (i * 8)

    return ret


def is_bit_flagged(data, flag_bit):
    return (data & flag_bit) != flag_bit

GLOBAL_VAR = [1, 2, 3]
