def match_test(a,b):
  match a+b:
    case 1:
      return 1
    case 2:
      return 2
    case 3:
      return 3
    case 99999:
      if eval('a-b') < 0:
        return 100
      return 99
    case _:
      return -1