operator_precedence = {
	'var': 0,
	'pow': 1,
	'mul': 2,
	'div': 2,
	'schur': 2,
	'add': 3,
	'sub': 3,
	'neg': 3,
	'kron': 2,
	'vec': 0
}
operator_repr = {
	'var': '',
	'pow': '^',
	'mul': ' ',
	'div': ' / ',
	'schur': ' * ',
	'add': ' + ',
	'sub': ' - ',
	'neg': '-',
	'kron': u' \u2297 ',
	'vec': 'vec'
}
operator_arity = {
	'var': 1,
	'pow': 2,
	'mul': 2,
	'div': 2,
	'schur': 2,
	'add': 2,
	'sub': 2,
	'neg': 1,
	'kron': 2,
	'vec': 1
}
def scalar(name): pass

class expr(object):
	def __init__(self, operator, symbol, precedence, rows=scalar('n'), cols=scalar('m'), symmetric=False):
		self._operator = operator
		self._symbol = symbol
		self._precedence = precedence
		self._rows = rows
		self._cols = cols
		self._symmetric = symmetric

	@property
	def operator(self): return self._operator
	@property
	def symbol(self): return self._symbol
	@property
	def precedence(self): return self._precedence
	@property
	def rows(self): return self._rows
	@property
	def cols(self): return self._cols	
	@property
	def symmetric(self): return self._symmetric	

	def __mul__(self, other):
		return mult(self,other)

class unaryexpr(expr):
	def __init__(self, operator, symbol, precedence, operand, rows=scalar('n'), cols=scalar('m'), symmetric=False):
		expr.__init__(self, operator, symbol, precedence, rows=rows, cols=cols, symmetric=symmetric)
		self._operand = operand

	@property
	def operand(self): return self._operand

	def __str__(self):
		if isinstance(self.operand, expr) and self.operand.precedence >= self.precedence:
			return '%s(%s)' % (self.symbol, self.operand.__str__())
		else:
			return '%s%s' % (self.symbol, self.operand.__str__())

	def __repr__(self):
		return '(%s[%sx%s%s] %s)' % (self.operator, self.rows, self.cols, ' Sym' if self.symmetric == True else '', self.operand.__repr__())

	def __eq__(self, other):
		return self.operator == other.operator and self.operand == other.operand

class binaryexpr(expr):
	def __init__(self, operator, symbol, precedence, left, right, rows=scalar('n'), cols=scalar('m'), symmetric=False):
		expr.__init__(self, operator, symbol, precedence, rows=rows, cols=cols, symmetric=symmetric)
		self._left = left
		self._right = right

	@property
	def left(self): return self._left
	@property
	def right(self): return self._right
	
	def __str__(self):
		if isinstance(self.left, expr) and self.left.precedence >= self.precedence:
			s = '(%s)%s' % (self.left.__str__(), self.symbol)
		else:
			s = '%s%s' % (self.left.__str__(), self.symbol)
		if isinstance(self.right, expr) and self.right.precedence >= self.precedence:
			s = '%s(%s)' % (s, self.right.__str__())
		else:
			s = '%s%s' % (s, self.right.__str__())
		return s

	def __repr__(self):
		return '(%s[%sx%s%s] %s %s)' % (self.operator, self.rows, self.cols, ' Sym' if self.symmetric == True else '', self.left.__repr__(), self.right.__repr__())

def var(name):
	return unaryexpr('var', '', 0, name)

def matrix(name, rows=scalar('n'), cols=scalar('m'), symmetric=False):
	return unaryexpr('var', '', 0, name, rows=rows, cols=cols, symmetric=symmetric)

def vector(name, rows=scalar('n')):
	return unaryexpr('var', '', 0, name, rows=rows, cols=1, symmetric=False)

def scalar(name):
	return unaryexpr('var', '', 0, name, rows=1, cols=1, symmetric=True)

def vec(e):
	return unaryexpr('vec', 'vec', 0, e, rows=e.rows * e.cols, cols=1, symmetric=False)

def t(e):
	return unaryexpr('transpose', 't', 0, e, rows=e.cols, cols=e.rows, symmetric=e.symmetric)

def mult(left, right):
	assert left.cols == right.rows, 'Operator mult, matrices '+left.__repr__()+' and '+right.__repr__()+' are incompatible'
	# TODO Symmetric if left == t(right)
	return binaryexpr('mult', '', 1, left, right, rows=left.rows, cols=right.cols, symmetric=False)