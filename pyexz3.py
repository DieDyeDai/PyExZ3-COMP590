# Copyright: see copyright.txt

import os
import sys
import logging
import traceback
import subprocess
from optparse import OptionParser

from symbolic.loader import *
from symbolic.explore import ExplorationEngine

print("PyExZ3 (Python Exploration with Z3)")

sys.path = [os.path.abspath(os.path.join(os.path.dirname(__file__)))] + sys.path

usage = "usage: %prog [options] <path to a *.py file>"
parser = OptionParser(usage=usage)

parser.add_option("-l", "--log", dest="logfile", action="store", help="Save log output to a file", default="")
parser.add_option("-s", "--start", dest="entry", action="store", help="Specify entry point", default="")
parser.add_option("-g", "--graph", dest="dot_graph", action="store", help="Generate a DOT graph of execution tree", default="")
parser.add_option("-m", "--max-iters", dest="max_iters", type="int", help="Run specified number of iterations", default=0)
parser.add_option("--cvc", dest="cvc", action="store_true", help="Use the CVC SMT solver instead of Z3", default=False)
parser.add_option("--z3", dest="cvc", action="store_false", help="Use the Z3 SMT solver")

(options, args) = parser.parse_args()

if not (options.logfile == ""):
	logging.basicConfig(filename=options.logfile,level=logging.DEBUG)
	

if len(args) == 0 or not os.path.exists(args[0]):
	parser.error("Missing app to execute")
	sys.exit(1)

solver = "cvc" if options.cvc else "z3"

filename = os.path.abspath(args[0])

prepend_eval = """
import builtins
import inspect
def eval(arg, globals=0, locals=0):
  builtins._eval_within_file = True

  previous_call_frame = inspect.stack()[1][0]
  
  _globals = previous_call_frame.f_globals if (globals == 0) else globals
  _locals = previous_call_frame.f_locals if (locals == 0) else locals
  
  res = builtins.eval(arg, _globals, _locals)

  builtins._eval_within_file = False

  return res

def exec(arg, /, globals=0, locals=0, *, closure=None):
  builtins._exec_within_file = True

  previous_call_frame = inspect.stack()[1][0]
  
  _globals = previous_call_frame.f_globals if (globals == 0) else globals
  _locals = previous_call_frame.f_locals if (locals == 0) else locals
  
  builtins.exec(arg, _globals, _locals, closure=closure)

  builtins._exec_within_file = False


"""

appended_filename = '_explore.py'

with open(filename, 'r') as _f:
	with open(appended_filename, 'w+') as f:
		content = _f.read()
		f.seek(0,0)
		f.write(prepend_eval)
		f.write(content)

# Get the object describing the application
app = loaderFactory(appended_filename,options.entry)
if app == None:
	sys.exit(1)

print ("Exploring " + app.getFile() + "." + app.getEntry())

result = None
try:
	engine = ExplorationEngine(app.createInvocation(), solver=solver)

	generatedInputs, returnVals, path = engine.explore(options.max_iters)
	# check the result
	result = app.executionComplete(returnVals)

	# output DOT graph
	if not (options.dot_graph == ""):
		file = open(options.dot_graph+".dot","w")
		file.write(path.toDot())
		file.close()

		# run_dot_string = "dot -Tsvg " + options.dot_graph+".dot -o " + options.dot_graph + ".svg"
		# print(run_dot_string)
		# subprocess.run(run_dot_string)

except ImportError as e:
	# createInvocation can raise this
	logging.error(e)
	sys.exit(1)

if result == None or result == True:
	sys.exit(0)
else:
	sys.exit(1)