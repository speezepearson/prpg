#!/usr/bin/python

'''The canonical implementation of the `pow` pseudo-random gobbledygook generator.

As a script, it reads a seed on standard input, and turns it into gobbledygook.

Everything else in this package is a nice user interface around this script.
'''

import hashlib
import argparse

def string_to_gobbledygook(s, charsets):
  sha = hashlib.sha256(s.encode('utf-8')).hexdigest()
  n = int(sha, 16)

  result = ''
  for charset in charsets:
    result += charset[n % len(charset)]
    n //= len(charset)

  charset = ''.join(charsets)
  while n > 0:
    result += charset[n % len(charset)]
    n //= len(charset)

  return result

# THESE ASSERTIONS SHOULD NEVER CHANGE:
# They are correct BY DEFINITION.
# Any implementation that produces different answers is necessarily wrong,
#  because adopting it would break backwards-compatibility.
_sample_charsets = ['abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', '0123456789', '!']
assert string_to_gobbledygook('foo', _sample_charsets) == 'wQ4!34PvMko0jV!jTLUVVCxIWkVT1THwWkmb5eY4htWid'
assert string_to_gobbledygook('foo bar', _sample_charsets) == 'rO8!Kwi7K5uzEE21icnpewdKHVjGIf0bvUkXgod3WVR4r'

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('charsets', nargs='+')
  args = parser.parse_args()

  s = input()

  print(string_to_gobbledygook(s), end='')
