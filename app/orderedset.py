
class OrderedSet:

    def __init__(self, initial=set()):
        self._data = dict.fromkeys(initial) 
    
    def add(self, item):
        self._data[item] = None

    def remove(self, item):
        self._data.pop(item, None)

    def union(self, other):
        return self._data.update(other._data)
    
    def difference(self, other):
        for item in other:
            self.remove(item) 
    
    def __iter__(self):
        return iter(self._data.keys())

    def __contains__(self, item):
        return item in self._data

    def __repr__(self):
        return repr(self._data.keys()) 

    