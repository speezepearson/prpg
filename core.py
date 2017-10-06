#!/usr/bin/python

'''The canonical implementation of the `pow` pseudo-random gobbledygook generator.

Reads a seed on standard input, and turns it into gobbledygook.

Everything else in this package is a nice user interface around this script.
'''

import hashlib
import argparse

CORRECT_HASH = '4ede6dd9545a96c99a50d4a14344a83b20da21adabc85b98912cb79e880c1776'
this_source_code = open(__file__).read()
assert hashlib.sha256(this_source_code.replace(CORRECT_HASH, '').encode('utf-8')).hexdigest() == CORRECT_HASH, 'for backwards-compatibility, this file should never change'

parser = argparse.ArgumentParser()
parser.add_argument('charsets', nargs='+')
args = parser.parse_args()

salted_seed = input()
sha = hashlib.sha256(salted_seed.encode('utf-8')).hexdigest()
n = int(sha, 16)

result = ''
for charset in args.charsets:
  result += charset[n % len(charset)]
  n //= len(charset)

charset = ''.join(args.charsets)
while n > 0:
  result += charset[n % len(charset)]
  n //= len(charset)

print(result, end='')
