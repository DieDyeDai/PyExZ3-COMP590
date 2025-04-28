
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


def match_test(a,b):
  match a+b:
    case 1:
      return 1
    case 2:
      return 2
    case 3:
      return 3
    case 99999:
      return 99999
    case _:
      return -1