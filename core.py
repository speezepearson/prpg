#!/usr/bin/python

'''The core of `pow`'s password generator.

This algorithm (and the password requirements) is all you need in order to recompute a password. The rest of this package is just a nice UI to this module.
'''

import hashlib
import hmac
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
