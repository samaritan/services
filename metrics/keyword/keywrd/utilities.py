def chunk(sequence, size):
    for index in range(0, len(sequence), size):
        yield sequence[index:index + size]
