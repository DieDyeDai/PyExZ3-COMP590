# Copyright: see copyright.txt

from symbolic.path_to_constraint import PathToConstraint
import utils
import inspect
import functools
import logging
import builtins

# the ABSTRACT base class for representing any expression that depends on a symbolic input
# it also tracks the corresponding concrete value for the expression (aka concolic execution)

log = logging.getLogger("se.z3")

class SymbolicType(object):
	def __init__(self, name, expr=None):
		self.name = name
		self.expr = expr

	# to be provided by subclass

	def getConcrValue(self):
		raise NotImplemented()

	def wrap(conc,sym):
		raise NotImplemented()

	# public funs

	def isVariable(self):
		return self.expr == None

	def unwrap(self):
		if self.isVariable():
			return (self.getConcrValue(),self)
		else:
			return (self.getConcrValue(),self.expr)

	def getVars(self):
		if self.isVariable():
			return [self.name]
		elif isinstance(self.expr,list):
			return self._getVarsLeaves(self.expr)
		else:
			return []

	def _getVarsLeaves(self,l):
		if isinstance(l,list):
			return functools.reduce(lambda a, x: self._getVarsLeaves(x) + a,l,[])
		elif isinstance(l,SymbolicType):
			return [l.name]
		else:
			return []

	# creating the expression tree
	def _do_sexpr(self,args,fun,op,wrap):
		tainted = False
		try:
			# If operations on symbolic types are being run within an eval/exec call, set the tainted flag on the current path constraint.
			if (builtins._eval_within_file):
				SymbolicObject.SI.current_constraint.tainted = True
				for a in args:
					if isinstance(a,SymbolicType):
						eval_warn_str = ("Eval with symbolic inputs: " +
							str(
								[(args[i].toString() if isinstance(args[i],SymbolicType) else args[i])
								for i in range(0, len(args))]
							) +
							"\nwith operation: " + op
						)
						log.warning(eval_warn_str)
						print(eval_warn_str)
						break
			if (builtins._exec_within_file):
				SymbolicObject.SI.current_constraint.tainted = True
				for a in args:
					if isinstance(a,SymbolicType):
						exec_warn_str = ("Exec with symbolic inputs: " +
							str(
								[(args[i].toString() if isinstance(args[i],SymbolicType) else args[i])
								for i in range(0, len(args))]
							) +
							"\nwith operation: " + op
						)
						log.warning(exec_warn_str)
						print(exec_warn_str)
						break
		except:
			pass
		finally:
			unwrapped = [ (a.unwrap() if isinstance(a,SymbolicType) else (a,a)) for a in args ]
			args = zip(inspect.getfullargspec(fun).args, [ c for (c,s) in unwrapped ])
			concrete = fun(**dict([a for a in args]))
			symbolic = [ op ] + [ s for c,s in unwrapped ]
			return wrap(concrete, symbolic)

	def symbolicEq(self, other):
		if not isinstance(other,SymbolicType):
			return False
		if self.isVariable() or other.isVariable():
			return self.name == other.name
		return self._eq_worker(self.expr,other.expr)

	def _eq_worker(self, expr1, expr2):
		if type(expr1) != type(expr2):
			return False
		if isinstance(expr1, list):
			return len(expr1) == len(expr2) and\
			       type(expr1[0]) == type(expr2[0]) and\
                               all([ self._eq_worker(x,y) for x,y in zip(expr1[1:],expr2[1:]) ])
		elif isinstance(expr1, SymbolicType):
			return expr1.name == expr2.name
		else:
			return expr1 == expr2

	def toString(self):
		if self.isVariable():
			return self.name + "#" + str(self.getConcrValue())
		else:
			return self._toString(self.expr)

	def _toString(self,expr):
		if isinstance(expr,list):
			return "(" + expr[0] + " " + ", ".join([ self._toString(a) for a in expr[1:] ]) + ")"
		elif isinstance(expr,SymbolicType):
			return expr.toString()
		else:
			return str(expr)

# this class is also ABSTRACT although __init__.py does
# initialize wrap to return SymbolicInteger for the 
# relational comparison operators

class SymbolicObject(SymbolicType,object): 
	def __init__(self, name, expr=None):
		SymbolicType.__init__(self,name,expr)

	SI : PathToConstraint = None    # this is set up by ConcolicEngine to link __bool__ to PathConstraint

	def wrap(conc,sym):
		# see __init__.py
		raise NotImplemented()

	# this is a critical interception point: the __bool__
	# method is called whenever a predicate is evaluated in
	# Python execution (if, while, and, or). This allows us
	# to capture the path condition

	def __bool__(self):
		ret = bool(self.getConcrValue())
		if SymbolicObject.SI != None:
			SymbolicObject.SI.whichBranch(ret,self)
		return ret

	# compute both the symbolic and concrete image of operator
	def _do_bin_op(self, other, fun, op, wrap):
		return self._do_sexpr([self,other], fun, op, wrap)

	def __eq__(self, other):
		# TODO: what it self is not symbolic and other is???
		return self._do_bin_op(other, lambda x, y: x == y, "==", SymbolicObject.wrap)

	def __ne__(self, other):
		return self._do_bin_op(other, lambda x, y: x != y, "!=", SymbolicObject.wrap)

	def __lt__(self, other):
		return self._do_bin_op(other, lambda x, y: x < y, "<", SymbolicObject.wrap)

	def __le__(self, other):
		return self._do_bin_op(other, lambda x, y: x <= y, "<=", SymbolicObject.wrap)

	def __gt__(self, other):
		return self._do_bin_op(other, lambda x, y: x > y, ">", SymbolicObject.wrap)

	def __ge__(self, other):
		return self._do_bin_op(other, lambda x, y: x >= y, ">=", SymbolicObject.wrap)


