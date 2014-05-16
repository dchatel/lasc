import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from collections import namedtuple

class LascException(Exception):
	def __init__(self, message):
		self._message = message
	def __str__(self):
		return self._message

def scalar(name): pass

class expr(object):
	def __init__(self, operator, symbol, precedence, rows=scalar('n'), cols=scalar('m')):
		self._operator = operator
		self._symbol = symbol
		self._precedence = precedence
		self._rows = rows
		self._cols = cols

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

	def __hash__(self):
		return hash(self.__repr__())
	def __eq__(self, other):
		return identic(self, other)
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
	def __init__(self, operator, symbol, precedence, operand, rows=scalar('n'), cols=scalar('m')):
		expr.__init__(self, operator, symbol, precedence, rows=rows, cols=cols)
		self._operand = operand

	@property
	def operand(self): return self._operand

	def __str__(self):
		if isinstance(self.operand, expr) and self.operand.precedence >= self.precedence:
			return '%s(%s)' % (self.symbol, self.operand.__str__())
		else:
			return '%s%s' % (self.symbol, self.operand.__str__())

	def __repr__(self):
		return u'(%s[%s\u00d7%s] %s)' % (self.operator, self.rows, self.cols, self.operand.__repr__())

class binaryexpr(expr):
	def __init__(self, operator, symbol, precedence, left, right, rows=scalar('n'), cols=scalar('m')):
		expr.__init__(self, operator, symbol, precedence, rows=rows, cols=cols)
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
		return u'(%s[%s\u00d7%s] %s %s)' % (self.operator, self.rows, self.cols, self.left.__repr__(), self.right.__repr__())

def scalar(name):
	return unaryexpr('var', '', 0, name, rows=1, cols=1)

def vector(name, rows=scalar('n')):
	return unaryexpr('var', '', 0, name, rows=rows, cols=1)

def matrix(name, rows=scalar('n'), cols=scalar('m')):
	return unaryexpr('var', '', 0, name, rows=rows, cols=cols)

def vec(e):
	return unaryexpr('vec', 'vec', 0, e, rows=e.rows * e.cols, cols=1)

def t(e):
	return unaryexpr('transpose', 't', 0, e, rows=e.cols, cols=e.rows)

def add(left, right):
	if isinstance(left, (int, long, float)): left = scalar(left)
	if isinstance(right, (int, long, float)): right = scalar(right)

	if is_scalar(left) or is_scalar(right):
		return binaryexpr('add', '+', 2, left, right, rows=max(left.rows, right.rows), cols=max(left.cols, right.cols))
	elif left.rows == right.rows and left.cols == right.cols:
		return binaryexpr('add', '+', 2, left, right, rows=left.rows, cols=left.cols)

	raise LascException('Operator add, incompatible matrices:\n%s\n%s' % (left.__repr__(), right.__repr__()))

def mult(left, right):
	if isinstance(left, (int, long, float)): left = scalar(left)
	if isinstance(right, (int, long, float)): right = scalar(right)

	if is_scalar(left) or is_scalar(right):
		return binaryexpr('mult', '', 1, left, right, rows=max(left.rows, right.rows), cols=max(left.cols, right.cols))
	elif left.cols == right.rows:
		return binaryexpr('mult', '', 1, left, right, rows=left.rows, cols=right.cols)

	raise LascException('Operator mult, incompatible matrices:\n%s\n%s' % (left.__repr__(),right.__repr__()))

def is_scalar(e):
	return isinstance(e, expr) and e.rows == 1 and e.cols == 1

def identic(a, b):
	if isinstance(a, unaryexpr) and isinstance(b, unaryexpr):
		return a.operator == b.operator and \
		identic(a.rows, b.rows) and \
		identic(a.cols, b.cols) and \
		identic(a.operand, b.operand)
	elif isinstance(a, binaryexpr) and isinstance(b, binaryexpr):
		return a.operator == b.operator and \
		identic(a.rows, b.rows) and \
		identic(a.cols, b.cols) and \
		identic(a.left, b.left) and \
		identic(a.right, b.right)
	else:
		return not isinstance(a, expr) and not isinstance(b, expr) and a == b

def match_exact(pattern, e):
	Answer = namedtuple('Answer','matched map')
	dic = {}

	def internal(pattern, e):
		equal = True
		# check valued scalars
		if isinstance(pattern, (int, long, float)) and isinstance(e, (int, long, float)):
			equal = pattern == e
		# check sizes
		elif isinstance(pattern, (int, long, float)) and isinstance(e, expr) and not(internal(e.rows, 1) and internal(e.cols, 1)):
			equal = False
		elif isinstance(e, (int, long, float)) and isinstance(pattern, expr) and not(internal(pattern.rows, 1) and internal(pattern.cols, 1)):
			equal = False
		elif isinstance(pattern, expr) and isinstance(e, expr) and not(internal(pattern.rows, e.rows) and internal(pattern.cols, e.cols)):
			equal = False

		elif pattern in dic:
			equal = identic(dic[pattern], e)

		elif isinstance(pattern, unaryexpr):
			if pattern.operator == 'var':
				dic[pattern] = e
				equal = True
			else: equal = pattern.operator == e.operator and internal(pattern.operand, e.operand)
		else: equal = isinstance(pattern, binaryexpr) and isinstance(e, binaryexpr) and pattern.operator == e.operator and internal(pattern.left, e.left) and internal(pattern.right, e.right)
		return equal

	answer = internal(pattern, e)
	return Answer(answer, dic)

def count(pattern, e):
	total = 1 if match_exact(pattern, e).matched else 0
	if isinstance(e, unaryexpr): total += count(pattern, e.operand)
	elif isinstance(e, binaryexpr): total += count(pattern, e.left) + count(pattern, e.right)
	return total

def matchall(pattern, e):
	matches = []

	def internal(pattern, e):
		m = match_exact(pattern, e)
		if m.matched: matches.append(m.map)
		if isinstance(e, unaryexpr): internal(pattern, e.operand)
		elif isinstance(e, binaryexpr):
			internal(pattern, e.left)
			internal(pattern, e.right)

	internal(pattern, e)
	return matches

def rewrite(rewrited, dic):
	if rewrited in dic:
		return dic[rewrited]
	elif isinstance(rewrited, unaryexpr):
		return unaryexpr(rewrited.operator, rewrited.symbol, rewrited.precedence, rewrite(rewrited.operand, dic), rows=rewrite(rewrited.rows, dic), cols=rewrite(rewrited.cols, dic))
	elif isinstance(rewrited, binaryexpr):
		return unaryexpr(rewrited.operator, rewrited.symbol, rewrited.precedence, rewrite(rewrited.left, dic), rewrite(rewrited.right, dic), rows=rewrite(rewrited.rows, dic), cols=rewrite(rewrited.cols, dic))

def reduceall(original, rewrited, e):
	m = match_exact(original, e)
	if m.matched:
			return rewrite(rewrited, m)
	if isinstance(e, unaryexpr):
		return unaryexpr(e.operator, e.symbol, e.precedence, reduceall(original, rewrited, e.operand), reduceall(original, rewrited, e.rows), reduceall(original, rewrited, e.cols))
	elif isinstance(e, binaryexpr):
		return binaryexpr(e.operator, e.symbol, e.precedence, reduceall(original, rewrited, e.left), reduceall(original, rewrited, e.right), reduceall(original, rewrited, e.rows), reduceall(original, rewrited, e.cols))