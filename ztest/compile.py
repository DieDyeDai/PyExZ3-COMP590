with open("C:\\repo\\PyExZ3\\ztest\\eval.py", "r") as file:
  content = file.read()

import ast

p = ast.parse(content)

print(ast.dump(p, True, True, indent=2))