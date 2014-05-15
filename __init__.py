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
		return '(%s[%sx%s] %s)' % (self.operator, self.rows, self.cols, self.operand.__repr__())

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
		return '(%s[%sx%s] %s %s)' % (self.operator, self.rows, self.cols, self.left.__repr__(), self.right.__repr__())

def scalar(name):
	return unaryexpr('var', '', 0, name, rows=1, cols=1)
def scalartok(name):
	return unaryexpr('tok', '', 0, name, rows=1, cols=1)

def vector(name, rows=scalar('n')):
	return unaryexpr('var', '', 0, name, rows=rows, cols=1)
def vectortok(name, rows=scalartok('n')):
	return unaryexpr('tok', '', 0, name, rows=rows, cols=1)

def matrix(name, rows=scalar('n'), cols=scalar('m')):
	return unaryexpr('var', '', 0, name, rows=rows, cols=cols)
def matrixtok(name, rows=scalartok('n'), cols=scalartok('m')):
	return unaryexpr('tok', '', 0, name, rows=rows, cols=cols)

def smatrix(name, rows=scalar('n')):
	return unaryexpr('var', '', 0, name, rows=rows, cols=rows)
def smatrixtok(name, rows=scalartok('n')):
	return unaryexpr('tok', '', 0, name, rows=rows, cols=rows)

def vec(e):
	return unaryexpr('vec', 'vec', 0, e, rows=e.rows * e.cols, cols=1)

def t(e):
	return unaryexpr('transpose', 't', 0, e, rows=e.cols, cols=e.rows)

def add(left, right):
	if isinstance(left, expr) and isinstance(right, expr):
		if left.cols != right.cols or left.rows != right.rows:
			raise LascException('Operator add, incompatible matrices:\n%s\n%s' % (left.__repr__(), right.__repr__()))
		return binaryexpr('add', '+', 2, left, right, rows=left.rows, cols=left.cols)
	elif isinstance(left, expr) and isinstance(right, (int, long, float)):
		return binaryexpr('add', '+', 2, left, right, rows=left.rows, cols=left.cols)
	elif isinstance(right, expr) and isinstance(left, (int, long, float)):
		return binaryexpr('add', '+', 2, left, right, rows=right.rows, cols=right.cols)
	else:
		raise LascException('Invalid operation `add` between %s and %s' % (left.__repr__(), right.__repr__()))

def mult(left, right):
	if isinstance(left, expr) and isinstance(right, expr):
		if left.cols != right.rows:
			raise LascException('Operator mult, incompatible matrices:\n%s\n%s' % (left.__repr__(),right.__repr__()))
		return binaryexpr('mult', '', 1, left, right, rows=left.rows, cols=right.cols)
	elif isinstance(left, expr) and isinstance(right, (int, long, float)):
		return binaryexpr('mult', '', 1, left, right, rows=left.rows, cols=left.cols)
	elif isinstance(right, expr) and isinstance(left, (int, long, float)):
		return binaryexpr('mult', '', 1, left, right, rows=right.rows, cols=right.cols)
	else:
		raise LascException('Invalid operation `mult` between %s and %s' % (left.__repr__(), right.__repr__()))

class matcher(object):
	def __init__(self):
		super(matcher, self).__init__()
		self.dic = {}

	def equality(self, a, b, showproof=False, depth=0):
		if showproof:
			print '%sTesting %s = %s' % ((' ' * depth*2), a, b)
		if a in self.dic:
			if showproof:
				print '%sRecall %s = %s' % ((' ' * depth*2), a, self.dic[a])
			return self.equality(self.dic[a], b, showproof, depth+1)
		if b in self.dic:
			if showproof:
				print '%sRecall %s = %s' % ((' ' * depth*2), b, self.dic[b])
			return self.equality(self.dic[b], a, showproof, depth+1)
		if a not in self.dic and isinstance(a, unaryexpr) and a.operator == 'tok' and (isinstance(b, (int, long, float)) and (self.equality(a.rows, 1, showproof, depth+1) and self.equality(a.cols, 1, showproof, depth+1)) or (isinstance(b, expr) and b.operator != 'tok' and self.equality(b.rows, a.rows, showproof, depth+1) and self.equality(b.cols, a.cols, showproof, depth+1))):
			if showproof:
				print '%sLet %s = %s' % ((' '*depth*2), a, b)
			self.dic[a] = b
			return True
		if b not in self.dic and isinstance(b, unaryexpr) and b.operator == 'tok' and (isinstance(a, (int, long, float)) and (self.equality(b.rows, 1, showproof, depth+1) and self.equality(b.cols, 1, showproof, depth+1)) or (isinstance(a, expr) and a.operator != 'tok' and self.equality(a.rows, b.rows, showproof, depth+1) and self.equality(a.cols, b.cols, showproof, depth+1))):
			if showproof:
				print '%sLet %s = %s' % ((' '*depth*2), b, a)
			self.dic[b] = a
			return True
		if isinstance(a, unaryexpr) and a.operator == 'tok' and isinstance(b, unaryexpr) and b.operator == 'tok' and a.operand == b.operand:
			if showproof:
				print '%s%s = %s' % ((' '*depth*2), a, b)
			return True
		if isinstance(a, (int, long, float)) and isinstance(b, (int, long, float)):
			if showproof:
				print '%s%s %s %s' % ((' '*depth*2), a, '=' if a == b else u'\u2260', b)
			return a == b
		if isinstance(a, unaryexpr) and a.operator == 'var' and isinstance(b, unaryexpr) and b.operator == 'var' and a.operand == b.operand:
			if showproof:
				print '%s%s = %s' % ((' '*depth*2), a, b)
			return True
		if isinstance(a, unaryexpr) and isinstance(b, unaryexpr) and a.operator == b.operator and self.equality(a.operand, b.operand, showproof, depth+1):
			if showproof:
				print '%s%s = %s' % ((' '*depth*2), a, b)
			return True
		if isinstance(a, binaryexpr) and isinstance(b, binaryexpr) and a.operator == b.operator and self.equality(a.left, b.left, showproof, depth+1) and self.equality(a.right, b.right, showproof, depth+1):
			if showproof:
				print '%s%s = %s' % ((' '*depth*2), a, b)
			return True
		if showproof:
			print u'%s%s \u2260 %s' %((' '*depth*2), a, b)
		return False