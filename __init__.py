import json

from .core import string_to_gobbledygook
from .choose import infer_choice
from .charspecs import chars_matching_charspec
from .clipboard import copy_to_clipboard
from .getseed import get_seed
from .rot13 import rot13

def seed_and_salt_to_gobbledygook(seed, salt_name, info):
  desired_length = info.get('length', 16)
  charset_specs = info.get('charset_specs', ['a-z', 'A-Z', '0-9', '!'])
  charsets = [chars_matching_charspec(spec) for spec in charset_specs]
  postprocess = eval(info['postprocess']) if 'postprocess' in info else (lambda gob: gob[:desired_length])
  salt = info.get('salt', salt_name)
  return postprocess(string_to_gobbledygook(seed + ' ' + salt, charsets))


def load_salts(f):
  if hasattr(f, 'read'):
    return json.loads(rot13(f.read()))
  else:
    with open(f) as true_f:
      return load_salts(true_f)
def dump_salts(f, salts):
  payload = rot13(json.dumps(salts, sort_keys=True, indent='  '))
  if hasattr(f, 'write'):
    f.write(payload)
  else:
    with open(f, 'w') as true_f:
      true_f.write(payload)
