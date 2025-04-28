def nested_test(a,b,c):
  x = 1 + 2
  y = 1 + a
  if (a == b):
    return f(a,b)
  return -99

def f(a,b):
  c = 1 + a
  if (a + b < c * c):
    d = eval('c+1')
    exec('print(a+b)')
    if (d > 0):
      return a+c
  c = eval('a-b')
  return a-c