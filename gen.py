
from itertools import product
import sys 

fp = open('comb.txt', 'w') 

sys.stdout = fp

for elm in product('ABEKMHOPCTYX', repeat=6):
    print(''.join(elm)) 
