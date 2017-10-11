#!/usr/bin/python

'''The core of `pow`'s password generator.

This algorithm (and the password requirements) is all you need in order to recompute a password. The rest of this package is just a nice UI to this module.

As a script (`python core.py --salt SALT --charsets CHARSET [CHARSET ...]`), this file reads a master-password from stdin, turns that into a key (using PBKDF2-HMAC-SHA256, with 10^5 iterations, salted with SALT), signs the empty string with that key (using HMAC-SHA256), and turns that MAC into a feasible password (see the package-level docs for details).

'''

import hashlib
import hmac
import argparse
from . import getseed
from typing import Sequence

def number_to_password(n: int, charsets: Sequence[str]) -> str:
  result = ''
  for charset in reversed(charsets):
    (n, i) = divmod(n, len(charset))
    result = charset[i] + result

  charset = ''.join(charsets)
  while n > 0:
    (n, i) = divmod(n, len(charset))
    result = charset[i] + result

  return result

def master_and_salt_to_password(master: str, salt: str, charsets) -> str:
  key = hashlib.pbkdf2_hmac(
          hash_name='sha256',
          password=master.encode('utf-8'),
          salt=salt.encode('utf-8'),
          iterations=10**6)
  mac = hmac.new(key=key, msg=b'', digestmod=hashlib.sha256)
  n = int(mac.hexdigest(), 16)
  return number_to_password(n, charsets)

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--mangle-master', action='store_true', help='enter master password in a laborious, char-by-char-mangled way if you are worried about keyloggers')
  parser.add_argument('--salt', required=True)
  parser.add_argument('--charsets', nargs='+', required=True)
  args = parser.parse_args()

  master = (getseed.get_mangled_seed() if args.mangle_master else getseed.get_seed())

  print(master_and_salt_to_password(master, args.salt, args.charsets), end='')
