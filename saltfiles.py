import json
import string
import re
from .rot13 import rot13
from .core import master_and_salt_to_password
from .charsets import chars_matching_charspec

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

  print('Choose:')
  for (i, x) in enumerate(xs):
    print('  {}. {}'.format(i, x))

  return xs[int(input('Your choice: '))]

def master_and_salt_and_saltinfo_to_password(master, salt, salt_info):
  charset_specs = salt_info.get('charsets', ['a-z', 'A-Z', '0-9', '!'])
  charsets = [chars_matching_charspec(spec) for spec in charset_specs]

  postprocess = eval(salt_info['postprocess']) if 'postprocess' in salt_info else (lambda password: password[-16:])

  if 'salt' in salt_info:
    salt = salt_info['salt']

  return postprocess(master_and_salt_to_password(master, salt, charsets))
