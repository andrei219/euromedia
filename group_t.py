from operator import attrgetter
from itertools import groupby

keyfunc = attrgetter('item', 'condition', 'spec')

class Register:

    def __init__(self, sn, item, condition, spec, line):
        self.sn = sn
        self.item = item
        self.condition = condition
        self.spec = spec
        self.line = line 

    def __str__(self):
        return ' '.join(str(v) for v in self.__dict__.values())
    
class ProcessedDevicesStore:

    def __init__(self):
        self.container = []

    
    def add(self, sn, item, condition, spec, line):
        for c in self.container:
            if c.sn == sn:
                break
        else:
            r = Register(sn, item, condition, spec, line)
            self.container.append(r)

    
    

    def __iter__(self):
        return iter(sorted(self.container, key=keyfunc) )

if __name__ == '__main__':

    p = ProcessedDevicesStore() 

    import random as rd
    for i in range(10):
        sn = rd.randint(0, 50) 
        item = rd.choice(['A', 'B', 'C'])
        condition = rd.choice(['NEW', 'USED'])
        spec = rd.choice(['EEUU', 'JAPAN'])
        line = rd.randint(1, 3)

        p.add(sn, item, condition, spec, line) 

    
    for _ in p:
        print(_)

    print('_' * 100)


    

    keyfunc = attrgetter('item', 'condition', 'spec')

    for key, group in groupby(p, key=keyfunc):
        print(key)
        for g in group:
            print(g)