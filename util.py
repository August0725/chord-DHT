import hashlib

m = 7

def get_hash(key):
    return int(hashlib.sha256(key.encode()).hexdigest(), 16) % pow(2, m)


def between_include_right(key, a, b):
    return between(key, a, b) or key == b

def between(key, a, b):
    if a > b:
        return not(b <= key <= a)
    elif a < b:
        return a < key < b
    else:
        return a != key