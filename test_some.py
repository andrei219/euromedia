
class Vector:

	def __init__(self, value, times):
		self.value = value
		self.times = times

	def __add__(self, other):
		if other.value != self.value:
			raise TypeError('Cant operate these values')
		else:
			return Vector(other.value, times=self.times + other.times)

	def __repr__(self):
		cls_name = self.__class__.__name__
		return f'{cls_name}(value={self.value}, times={self.times})'

if __name__ == '__main__':

	a = Vector('a', 2)
	b = Vector('a', 3)

	c = a + b

	print(c)

	assert c.times == a.times + b.times
	assert c.value == a.value == b.value
