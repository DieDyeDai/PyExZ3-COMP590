# Hooking into PyExZ3 to catch symbolic uses of eval/exec

This fork modifies PyExZ3 to detect when `eval` or `exec` are called within a Python function that lead to symbolic inputs (inputs that may be user- or attacker-controlled) being executed or operated on.

## Modifications:

- minor

`inspect.getargspec` is replaced by `inspect.getfullargspec` due to a different Python version being used in this fork.

- `pyexz3.py`

The main change is that, before running the symbolic execution engine on a Python function, it prepends code to redefine `eval` and `exec` within the scope of the module being tested.

The modified `eval`/`exec` functions set global flags accessible to the entire call stack (the builtins module) and pass in whatever global and local scopes were originally passed into `eval`/`exec` (the scopes of the previous stack frame, or the provided scopes). The global flags are read when operations on symbolic objects are executed in `symbolic_type.py` to check if the operation is being executed within an `eval`/`exec`.

- `constraint.py`, `path_to_constraint.py`

A member variable `tainted` is added to the `Constraint` class. This is set when a symbolic `eval`/`exec` is detected, and is output into the generated `.dot` file in the `_toDot` method in the `PathToConstraint` class.

- `symbolic_type.py`

When a symbolic expression is being evaluated (in `_do_sexpr`), the flags set by the modified `eval`/`exec` code are read, one for `eval` and one for `exec`. If either is true and it detects symbolic types in the input to the operation, it flags the current path constraint as tainted and outputs the arguments into the log file.