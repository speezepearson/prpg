#!/usr/bin/python

'''The core of PRPG's algorithm.

This algorithm (and the salt, and your master password) is all you need in order to recompute a password. The rest of this package is just a nice UI to this module.
'''

import hashlib
import base64
from pathlib import Path

wordlist = list(sorted([l.strip() for l in (Path(__file__).parent/'wordlist.txt').open()]))
assert len(wordlist) == 2048

def master_and_salt_to_password(master: str, salt: str, nwords: int = 6):
  key = hashlib.pbkdf2_hmac(
          hash_name='sha256',
          password=master.encode('utf-8'),
          salt=salt.encode('utf-8'),
          iterations=10**6)
  sha = hashlib.sha256(key).digest()
  n = int.from_bytes(sha, byteorder='big')
  words = []
  for _ in range(nwords):
    n, r = divmod(n, 2048)
    words.append(wordlist[r])
  return ''.join(w[0].upper() + w[1:] for w in words) + '0!'
