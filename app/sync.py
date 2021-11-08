



from collections.abc import Iterable

l = [1, 2, {3, 4}, [3, 4, [1, 2]]]


def flatten(iterable):
    for element in iterable:
        if isinstance(element, Iterable):
            yield from flatten(element)
        else:
            yield element

if __name__ == '__main__':

    for e in flatten(l):
        print(e)

    