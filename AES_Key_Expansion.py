RCON = [0x00, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36]

def rotate_bytes(key):
    return key[1:] + key[:1]

def substitution_box(key, SBOX):
    return [SBOX[b] for b in key]

def key_expansion(key, SBOX):
    key_chars = list(key)
    assert len(key_chars) == 16

    key_schedule = [key_chars[i:i+4] for i in range(0,16,4)]

    for i in range(4, 44):
        temp = key_schedule[i - 1]
        if i % 4 == 0:
            temp = substitution_box(rotate_bytes(temp), SBOX)
            temp[0] ^= RCON[i // 4]
        new_key = [a ^ b for a, b in zip(key_schedule[i - 4], temp)]
        key_schedule.append(new_key)
    return key_schedule
