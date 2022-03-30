from __future__ import print_function
import json
import string
import re
import sys
from .core import master_and_salt_to_password

def load_salts(path):
  with open(path) as f:
    return json.loads(f.read())

def dump_salts(path, salts):
  payload = json.dumps(salts, sort_keys=True, indent=2)
  with open(path, 'w') as f:
    f.write(payload)
    f.write('\n')

def fuzzy_search(salts, queries):
  query = '.*'.join(queries)
  return [key for key in salts if re.match(query, key)]

def disambiguate(xs):
  xs = list(sorted(xs))

  if len(xs) == 0:
    raise ValueError('no matches')
  elif len(xs) == 1:
    return xs[0]

  options = {str(i): x for i, x in enumerate(xs, start=1)}

  print('Options:', file=sys.stderr)
  for i, x in options.items():
    print('  {}: {}'.format(i, x), file=sys.stderr)

  response = input('Choose an option: ')
  while response not in options:
    response = input('Invalid response. Try again: ')

  return options[response]


def master_and_salt_and_saltinfo_to_password(master, salt, salt_info):
  return master_and_salt_to_password(
    master=master,
    salt=salt_info.get('__salt__', salt),
    **({'maxlen': eval(salt_info['__maxlen__'])} if '__maxlen__' in salt_info else {}))
