def infer_choice(xs):
  xs = list(sorted(xs))

  if len(xs) == 0:
    raise ValueError('no matches')
  elif len(xs) == 1:
    return xs[0]

  print('Choose:')
  for (i, x) in enumerate(xs):
    print('  {}. {}'.format(i, x))

  return xs[int(input('Your choice: '))]
