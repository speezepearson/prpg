import json
import string
import re
import sys
from .rot13 import rot13
from .core import master_and_salt_to_password

def load_salts(path):
  with open(path) as f:
    return json.loads(rot13(f.read()))

def dump_salts(path, salts):
  payload = rot13(json.dumps(salts, sort_keys=True, indent='  '))
  with open(path, 'w') as f:
    f.write(payload)
    f.write('\n')

def fuzzy_search(salts, query):
  return [key for key in salts if re.match(query, key)]

def disambiguate(xs):
  xs = list(sorted(xs))

  if len(xs) == 0:
    raise ValueError('no matches')
  elif len(xs) == 1:
    return xs[0]

  print('Options:', file=sys.stderr)
  for (i, x) in enumerate(xs):
    print('  {}. {}'.format(i+1, x), file=sys.stderr)

  print('Choose an option: ', end='', file=sys.stderr)
  while True:
    try:
      return xs[int(input())-1]
    except (ValueError, IndexError):
      print('Invalid response. Try again: ', end='', file=sys.stderr)


def master_and_salt_and_saltinfo_to_password(master, salt, salt_info):
  return master_and_salt_to_password(
    master=master,
    salt=salt_info.get('__salt__', salt),
    **({'postprocess': eval(salt_info['__postprocess__'])}
       if '__postprocess__' in salt_info
       else {}))
