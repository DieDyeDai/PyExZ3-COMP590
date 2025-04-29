def match_test(a,b):
  match a+b:
    case 1:
      exec('print(f"Uncaught exec! {a},{b}")')
      return 1
    case 2:
      return 2
    case 3:
      return 3
    case 99999:
      if eval('a-b') < 0:
        if (b < 0):
          return 9
        else:
          return 10
      return 99
    case 100000:
      if eval('a' + '+b') == 0:
        return 100000
      return 101
    case 0.5:
      return 0.5
    case _:
      return -1