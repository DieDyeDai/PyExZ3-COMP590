def while_test(a,b,c):
  i = 0
  if c < 0:
    c*=1
  while i < c:
    a += 1
    if a > 10:
      return i
    i += 1