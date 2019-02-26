def group(iterable, n):
    args = [iter(iterable)] * n
    return zip(*args)
