


from itertools import permutations


l = ['asked', 'purchased', 'processed']


def perms(l, s1, s2):

    for perm in permutations(l):
        perm = list(perm)
        perm.insert(1, s1)
        perm.insert(3, s2)
        print(' '.join(perm))

if __name__ == '__main__':

    perms(l, '<', '=')
    perms(l, '=', '<')
    perms(l, '>', '=')
    perms(l, '=', '>')