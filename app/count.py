

from random import randint

if __name__ == '__main__':
    count = 0 
    import os 
    for file in os.listdir():
        if not file.startswith('ui_') and file.endswith('.py') and '_rc' not in file or \
            file.endswith('.qrc'):
            with open(file, 'r') as fp:
                lines = [line.strip('\n ') for line in fp if line]
                for line in lines:
                    if line:
                        count += 1

    print('Code written:', count, 'lines.')
    guis_files = [file for file in os.listdir() if file.startswith('ui_')]
    print('Guis designed:', len(guis_files), end='')
    print('.')


    l = [i for i in range(10)]
    def partailize(numbers, target):
        total = 0
        for i, n in enumerate(l):
            if total <= target: 
                total += n 
                if total > target:
                    numbers[i] = n + target - total
                    continue
            if total > target:
                numbers[i] = 0
