def get_max(numbers):
    ints = []
    for n in numbers:
        try:
            ints.append(int(n))
        except ValueError:
            pass
    return ints and max(ints) or None
