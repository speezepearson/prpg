#!/usr/bin/python3

import pprint
import json
import argparse
import os
import subprocess
import re
import sys


def rot13(s):
  return ''.join(
    chr(ord('a') + ((ord(c)+13-ord('a')) % 26)) if ord('a') <= ord(c) <= ord('z') else
    chr(ord('A') + ((ord(c)+13-ord('A')) % 26)) if ord('A') <= ord(c) <= ord('Z') else
    c
    for c in s)

def get_pow_output():
  (raw, _) = subprocess.Popen(['pow', seed], stdout=subprocess.PIPE).communicate()
  print()
  return raw.decode().strip()
def camel_case_bang(s):
  return ''.join(w[0].upper() + w[1:].lower() for w in s.split(' ')[:4]) + '!'
def infer_index(xs):
  if len(xs) == 0:
    raise ValueError('no matches')
  elif len(xs) == 1:
    return 0

  print('Choose:')
  for (i, x) in enumerate(xs):
    print('  {}. {}'.format(i, x))

  return int(input('Your choice: '))


parser = argparse.ArgumentParser()
parser.add_argument('-f', '--salts-file', default=os.path.join(os.environ['HOME'], '.salts.json'))
parser.add_argument('-i', '--get-info', action='store_true')
parser.add_argument('--no-rot13', action='store_false', dest='rot13')
parser.add_argument('queries', nargs='+')


if __name__ == '__main__':
  args = parser.parse_args()

  salts_json = open(args.salts_file).read()
  if args.rot13:
    salts_json = rot13(salts_json)
  info = json.loads(salts_json)

  query_pattern = '.*'.join(args.queries)

  matches = [(k, v) for (k, v) in info.items() if re.match(query_pattern, k)]

  try:
    match_index = infer_index([k for (k, v) in matches])
  except ValueError:
    print('no matches', file=sys.stderr)
    exit(1)

  (k, v) = matches[match_index]
  print('Match:', k)
  if args.get_info:
    pprint.pprint(v)
  seed = v.get("seed", k)
  pow_output = get_pow_output()
  final = camel_case_bang(pow_output)
  subprocess.Popen(['xsel', '--input', '--clipboard'], stdin=subprocess.PIPE).communicate(final.encode())
  if 'notes' in v:
    print('Notes:')
    pprint.pprint(v['notes'])
