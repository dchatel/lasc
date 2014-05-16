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

	def __hash__(self):
		return hash(self.__repr__())
		return hash(hashing().hash(self))
	def __eq__(self, other):
		return hashing().hash(self) == hashing().hash(other)
		#return matcher().equality(self, other)
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
#def scalartok(name):
#	return unaryexpr('tok', '', 0, name, rows=1, cols=1)

def vector(name, rows=scalar('n')):
	return unaryexpr('var', '', 0, name, rows=rows, cols=1)
#def vectortok(name, rows=scalartok('n')):
#	return unaryexpr('tok', '', 0, name, rows=rows, cols=1)

def matrix(name, rows=scalar('n'), cols=scalar('m')):
	return unaryexpr('var', '', 0, name, rows=rows, cols=cols)
#def matrixtok(name, rows=scalartok('n'), cols=scalartok('m')):
#	return unaryexpr('tok', '', 0, name, rows=rows, cols=cols)

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

class hashing(object):
	def __init__(self):
		super(hashing, self).__init__()
		self.dic = {}

	def hash(self, e):
		if isinstance(e, unaryexpr) and e.operator == 'var':
			if e.operand not in self.dic:
				self.dic[e.operand] = len(self.dic)
			return '(%s[%sx%s] %s)' % (e.operator, self.hash(e.rows), self.hash(e.cols), self.dic[e.operand])
		elif isinstance(e, unaryexpr):
			return '(%s[%sx%s] %s)' % (e.operator, self.hash(e.rows), self.hash(e.cols), self.hash(e.operand))
		elif isinstance(e, binaryexpr):
			return '(%s[%sx%s] %s %s)' % (e.operator, self.hash(e.rows), self.hash(e.cols), self.hash(e.left), self.hash(e.right))
		else:
			return e.__repr__()

def identic(a, b):
	if isinstance(a, unaryexpr) and isinstance(b, unaryexpr):
		return identic(a.rows, b.rows) and \
		identic(a.cols, b.cols) and \
		identic(a.operand, b.operand)
	elif isinstance(a, binaryexpr) and isinstance(b, binaryexpr):
		return identic(a.rows, b.rows) and \
		identic(a.cols, b.cols) and \
		identic(a.left, b.left) and \
		identic(a.right, b.right)
	else:
		return a == b

def match(pattern, e):
	dic = {}

	def internal(pattern, e):
		equal = True
		# check valued scalars
		if isinstance(pattern, (int, long, float)) and isinstance(e, (int, long, float)): equal = pattern == e
		# check sizes
		elif isinstance(pattern, (int, long, float)) and isinstance(e, expr) and not(internal(e.rows, 1) and internal(e.cols, 1)):
			print 'expression %s not scalar' % e
			equal = False
		elif isinstance(e, (int, long, float)) and isinstance(pattern, expr) and not(internal(pattern.rows, 1) and internal(pattern.cols, 1)):
			print 'pattern %s not scalar' % pattern
			equal = False
		elif isinstance(pattern, expr) and isinstance(e, expr) and not(internal(pattern.rows, e.rows) and internal(pattern.cols, e.cols)):
			print 'wrong size for %s and %s' % (pattern, e)
			equal = False

		elif pattern in dic:
			print '%s found in dic' % pattern
			equal = identic(dic[pattern], e)

		elif isinstance(pattern, unaryexpr):
			print '%s is unary' % pattern.__repr__()
			if pattern.operator == 'var':
				print 'Let %s = %s' % (pattern, e)
				dic[pattern] = e
				equal = True
			else: equal = pattern.operator == e.operator and internal(pattern.operand, e.operand)
		else: equal = isinstance(pattern, binaryexpr) and isinstance(e, binaryexpr) and pattern.operator == e.operator and internal(pattern.left, e.left) and internal(pattern.right, e.right)
		print '%s %s %s' % (pattern, '=' if equal else u'\u2260', e)
		return equal

	answer = internal(pattern, e)
	return (answer, dic)

#class matcher(object):
#	def __init__(self):
#		super(matcher, self).__init__()
#		self.dic = {}
#
#	def equality(self, a, b, showproof=False, depth=0):
#		if showproof:
#			print '%sTesting %s = %s' % ((' ' * depth), a, b)
#		if a in self.dic:
#			if showproof:
#				print '%sRecall %s = %s' % ((' ' * depth), a, self.dic[a])
#			return self.equality(self.dic[a], b, showproof, depth+2)
#		if b in self.dic:
#			if showproof:
#				print '%sRecall %s = %s' % ((' ' * depth), b, self.dic[b])
#			return self.equality(self.dic[b], a, showproof, depth+2)
#		if a not in self.dic and isinstance(a, unaryexpr) and a.operator == 'tok' and (isinstance(b, (int, long, float)) and (self.equality(a.rows, 1, showproof, depth+2) and self.equality(a.cols, 1, showproof, depth+2)) or (isinstance(b, expr) and b.operator != 'tok' and self.equality(b.rows, a.rows, showproof, depth+2) and self.equality(b.cols, a.cols, showproof, depth+2))):
#			if showproof:
#				print '%sLet %s = %s' % ((' ' * depth), a, b)
#			self.dic[a] = b
#			return True
#		if b not in self.dic and isinstance(b, unaryexpr) and b.operator == 'tok' and (isinstance(a, (int, long, float)) and (self.equality(b.rows, 1, showproof, depth+2) and self.equality(b.cols, 1, showproof, depth+2)) or (isinstance(a, expr) and a.operator != 'tok' and self.equality(a.rows, b.rows, showproof, depth+2) and self.equality(a.cols, b.cols, showproof, depth+2))):
#			if showproof:
#				print '%sLet %s = %s' % ((' ' * depth), b, a)
#			self.dic[b] = a
#			return True
#		if isinstance(a, unaryexpr) and a.operator == 'tok' and isinstance(b, unaryexpr) and b.operator == 'tok' and a.operand == b.operand:
#			if showproof:
#				print '%s%s = %s' % ((' ' * depth), a, b)
#			return True
#		if isinstance(a, (int, long, float)) and isinstance(b, (int, long, float)):
#			if showproof:
#				print '%s%s %s %s' % ((' ' * depth), a, '=' if a == b else u'\u2260', b)
#			return a == b
#		if isinstance(a, unaryexpr) and a.operator == 'var' and isinstance(b, unaryexpr) and b.operator == 'var' and a.operand == b.operand:
#			if showproof:
#				print '%s%s = %s' % ((' ' * depth), a, b)
#			return True
#		if isinstance(a, unaryexpr) and isinstance(b, unaryexpr) and a.operator == b.operator and self.equality(a.operand, b.operand, showproof, depth+2):
#			if showproof:
#				print '%s%s = %s' % ((' ' * depth), a, b)
#			return True
#		if isinstance(a, binaryexpr) and isinstance(b, binaryexpr) and a.operator == b.operator and self.equality(a.left, b.left, showproof, depth+2) and self.equality(a.right, b.right, showproof, depth+2):
#			if showproof:
#				print '%s%s = %s' % ((' ' * depth), a, b)
#			return True
#		if showproof:
#			print u'%s%s \u2260 %s' %((' ' * depth), a, b)
#		return False