import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class LascException(Exception):
	def __init__(self, message):
		self._message = message
	def __str__(self):
		return self._message

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

	def __eq__(self, other):
		return matcher().equality(self, other)
	def __ne__(self, other):
		return not self.__eq__(other)

	def __add__(self, other):
		return add(self, other)
	def __radd__(self, other):
		return add(other, self)
	def __mul__(self, other):
		return mult(self,other)
	def __rmul__(self, other):
		return mult(other, self)

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

def scalar(name):
	return unaryexpr('var', '', 0, name, rows=1, cols=1, symmetric=True)
def scalartok(name):
	return unaryexpr('tok', '', 0, name, rows=1, cols=1, symmetric=True)

def vector(name, rows=scalar('n')):
	return unaryexpr('var', '', 0, name, rows=rows, cols=1, symmetric=False)
def vectortok(name, rows=scalartok('n')):
	return unaryexpr('tok', '', 0, name, rows=rows, cols=1, symmetric=False)

def matrix(name, rows=scalar('n'), cols=scalar('m')):
	return unaryexpr('var', '', 0, name, rows=rows, cols=cols, symmetric=False)
def matrixtok(name, rows=scalartok('n'), cols=scalartok('m')):
	return unaryexpr('tok', '', 0, name, rows=rows, cols=cols, symmetric=False)

def smatrix(name, rows=scalar('n')):
	return unaryexpr('var', '', 0, name, rows=rows, cols=rows, symmetric=True)
def smatrixtok(name, rows=scalartok('n')):
	return unaryexpr('tok', '', 0, name, rows=rows, cols=rows, symmetric=True)

def vec(e):
	return unaryexpr('vec', 'vec', 0, e, rows=e.rows * e.cols, cols=1, symmetric=False)

def t(e):
	return unaryexpr('transpose', 't', 0, e, rows=e.cols, cols=e.rows, symmetric=e.symmetric)

def add(left, right):
	if isinstance(left, expr) and isinstance(right, expr):
		if left.cols != right.cols or left.rows != right.rows:
			raise LascException('Operator add, incompatible matrices:\n%s\n%s' % (left.__repr__(), right.__repr__()))
		return binaryexpr('add', '+', 2, left, right, rows=left.rows, cols=left.cols, symmetric=left.symmetric and right.symmetric)
	elif isinstance(left, expr) and isinstance(right, (int, long, float)):
		return binaryexpr('add', '+', 2, left, right, rows=left.rows, cols=left.cols, symmetric=left.symmetric)
	elif isinstance(right, expr) and isinstance(left, (int, long, float)):
		return binaryexpr('add', '+', 2, left, right, rows=right.rows, cols=right.cols, symmetric=right.symmetric)
	else:
		raise LascException('Invalid operation `add` between %s and %s' % (left.__repr__(), right.__repr__()))

def mult(left, right):
	if isinstance(left, expr) and isinstance(right, expr):
		if left.cols != right.rows:
			raise LascException('Operator mult, incompatible matrices:\n%s\n%s' % (left.__repr__(),right.__repr__()))
		return binaryexpr('mult', '', 1, left, right, rows=left.rows, cols=right.cols, symmetric=left==t(right))
	elif isinstance(left, expr) and isinstance(right, (int, long, float)):
		return binaryexpr('mult', '', 1, left, right, rows=left.rows, cols=left.cols, symmetric=left.symmetric)
	elif isinstance(right, expr) and isinstance(left, (int, long, float)):
		return binaryexpr('mult', '', 1, left, right, rows=right.rows, cols=right.cols, symmetric=right.symmetric)
	else:
		raise LascException('Invalid operation `mult` between %s and %s' % (left.__repr__(), right.__repr__()))

class matcher(object):
	def __init__(self):
		super(matcher, self).__init__()
		self.dic = {}

	def equality(self, a, b):
		if a in self.dic:
			return self.equality(self.dic[a], b)
		if b in self.dic:
			return self.equality(self.dic[b], a)
		if a not in self.dic and isinstance(a, unaryexpr) and a.operator == 'tok' and (isinstance(b, (int, long, float)) and (self.equality(a.rows, 1) and self.equality(a.cols, 1)) or (isinstance(b, expr) and self.equality(b.rows, a.rows) and self.equality(b.cols, a.cols))):
			self.dic[a] = b
			return True
		if b not in self.dic and isinstance(b, unaryexpr) and b.operator == 'tok' and (isinstance(a, (int, long, float)) and (self.equality(b.rows, 1) and self.equality(b.cols, 1)) or (isinstance(a, expr) and self.equality(a.rows, b.rows) and self.equality(a.cols, b.cols))):
			self.dic[b] = a
			return True
		if isinstance(a, (int, long, float)) and isinstance(b, (int, long, float)):
			return a == b
		if isinstance(a, unaryexpr) and a.operator == 'var' and isinstance(b, unaryexpr) and b.operator == 'var' and a.operand == b.operand:
			return True
		if isinstance(a, unaryexpr) and isinstance(b, unaryexpr) and a.operator == b.operator and self.equality(a.operand, b.operand):
			return True
		if isinstance(a, binaryexpr) and isinstance(b, binaryexpr) and a.operator == b.operator and self.equality(a.left, b.left) and self.equality(a.right, b.right):
			return True
		return False

	def replaceall(self, search, replace, e):
		if self.equality(e, search): return self.assigndic(replace)
		elif isinstance(e, unaryexpr): return unaryexpr(e.operator, e.symbol, e.precedence, self.replaceall(search, replace, e.operand), rows=e.rows, cols=e.cols, symmetric=e.symmetric)
		elif isinstance(e, binaryexpr): return binaryexpr(e.operator, e.symbol, e.precedence, self.replaceall(search, replace, e.left), self.replaceall(search, replace, e.right), rows=e.rows, cols=e.cols, symmetric=e.symmetric)
		else: return e

	def assigndic(self, e):
		if e in self.dic: return self.dic[e]
		elif isinstance(e, unaryexpr): return unaryexpr(e.operator, e.symbol, e.precedence, self.assigndic(e.operand), rows=self.assigndic(e.rows), cols=self.assigndic(e.cols), symmetric=e.symmetric)
		elif isinstance(e, binaryexpr): return binaryexpr(e.operator, e.symbol, e.precedence, self.assigndic(e.left), self.assigndic(e.right), rows=self.assigndic(e.rows), cols=self.assigndic(e.cols), symmetric=e.symmetric)
		else: return e