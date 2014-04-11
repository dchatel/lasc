operator_precedence = {
	'var': 0,
	'pow': 1,
	'mul': 2,
	'div': 2,
	'schur': 2,
	'add': 3,
	'sub': 3
}
operator_repr = {
	'var': '',
	'pow': '^',
	'mul': ' ',
	'div': ' / ',
	'schur': ' * ',
	'add': ' + ',
	'sub': ' - '
}

class expr(object):
	def __init__(self, operator, operands, negative=False):
		self._operator = operator
		self._operands = []
		for i in range(len(operands)):
			if isinstance(operands[i], expr) and operands[i].operator == self.operator:
				for j in range(len(operands[i].operands)):
					self._operands.append(operands[i].operands[j])
			else:
				self._operands.append(operands[i])
		self._negative = negative

	@property
	def operator(self):
	    return self._operator
	@operator.setter
	def operator(self, value):
	    self._operator = value

	@property
	def operands(self):
	    return self._operands
	@operands.setter
	def operands(self, value):
	    self._operands = value

	@property
	def negative(self):
	    return self._negative
	@negative.setter
	def negative(self, value):
	    self._negative = value

	@property
	def precedence(self):
	    return operator_precedence[self.operator]
	
	def __add__(self, other):
		return expr('add', [self, other])
	def __radd__(self, other):
		return expr('add', [other, self])
	def __sub__(self, other):
		return expr('sub', [self, other])
	def __rsub__(self, other):
		return expr('sub', [other, self])
	def __mul__(self, other):
		return expr('mul', [self, other])
	def __rmul__(self, other):
		return expr('mul', [other, self])
	def __div__(self, other):
		return expr('div', [self, other])
	def __rdiv__(self, other):
		return expr('div', [other, self])
	def __pow__(self, other):
		return expr('pow', [self, other])
	def __mod__(self, other):
		return expr('schur', [self, other])
	def __rmod__(self, other):
		return expr('schur', [other, self])
	def __pos__(self):
		return expr(self.operator, self.operands, self.negative)
	def __neg__(self):
		return expr(self.operator, self.operands, self.negative == False)

	def __str__(self):
		s = operator_repr[self.operator].join(map(lambda x: '(' + x.__str__() + ')' if isinstance(x, expr) and x.precedence >= self.precedence else x.__str__(), self.operands))
		if self.negative == True:
			if self.precedence > 0:
				return '-(' + s + ')'
			else:
				return '-' + s
		else:
			return s
	def __repr__(self):
		s = '(' + self.operator + ' ' + ' '.join(map(lambda x: x.__repr__(), self.operands)) + ')'
		if self.negative == True:
			return '-' + s
		else:
			return s

class var(expr):
	def __init__(self, name):
		expr.__init__(self, 'var', [name], False)
	#	
	#def __repr__(self):
	#	return self.name
	#def __str__(self):
	#	return self.name