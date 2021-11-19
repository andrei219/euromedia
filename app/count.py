

from random import randint

if __name__ == '__main__':
    count = 0 
    import os 
    for file in os.listdir():
        if not file.startswith('ui_') and file.endswith('.py') and '_rc' not in file:
            with open(file, 'r') as fp:
                lines = [line.strip('\n ') for line in fp if line]
                for line in lines:
                    if line:
                        count += 1

    print('You have written:', count, 'lines of code.')
    guis_files = [file for file in os.listdir() if file.startswith('ui_')]
    print('You have designed:', len(guis_files), 'guis.')


    l = [i for i in range(10)]
    def partailize(numbers, target):
        total, first = 0, True
        for i, n in enumerate(l):
            if total <= target: 
                total += n 
                if total > target:
                    numbers[i] = n + target - total
                    continue
            if total > target:
                numbers[i] = 0
