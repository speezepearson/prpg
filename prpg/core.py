#!/usr/bin/python

'''The core of PRPG's algorithm.

This algorithm (and the salt, and your master password) is all you need in order to recompute a password. The rest of this package is just a nice UI to this module.
'''

import hashlib
import base64

def master_and_salt_to_password(master: str, salt: str, postprocess=(lambda pw: pw[:16]+'Aa0+')) -> str:
  key = hashlib.pbkdf2_hmac(
          hash_name='sha256',
          password=master.encode('utf-8'),
          salt=salt.encode('utf-8'),
          iterations=10**6)
  sha = hashlib.sha256(key).digest()
  pw = base64.b64encode(sha).decode('utf-8')
  return postprocess(pw)
