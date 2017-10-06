#!/usr/bin/python3

import pprint
import json
import argparse
import os
import subprocess
import re
import sys
import os
import hashlib
import string

import pow

def determine_query_result(salts, query):
  result = pow.infer_choice([key for key in salts if re.match(query, key)])
  if sys.stdout.isatty():
    print('Chose:', result, file=sys.stderr)
  return result

def raw_main(args):
  print_or_copy = (print if args.print else pow.copy_to_clipboard)
  result = pow.core.string_to_gobbledygook(pow.get_seed(), [string.ascii_lowercase, string.ascii_uppercase, string.digits, '!'])
  print_or_copy(result)

def info_main(args):
  salts = pow.load_salts(args.salts_file)
  k = determine_query_result(salts.keys(), args.query)
  pprint.pprint(salts[k])

def gob_main(args):
  salts = pow.load_salts(args.salts_file)
  print_or_copy = (print if args.print else pow.copy_to_clipboard)
  k = determine_query_result(salts.keys(), args.query)
  seed = pow.get_seed()
  result = pow.seed_and_salt_to_gobbledygook(seed, k, salts[k])
  print_or_copy(result)

  if args.persistent:
    rot13_seed = pow.rot13(seed); del seed
    while True:
      query = input('Query: ')
      k = determine_query_result(salts.keys(), args.query)
      result = pow.seed_and_salt_to_gobbledygook(pow.rot13(rot13_seed), k, salts[k])
      print_or_copy(result)

def add_main(args):
  salts = pow.load_salts(args.salts_file)
  k = input('New key: ')
  salt = json.loads(input('New salt: '))
  salts[k] = salt
  pow.dump_salts(args.salts_file, salts)

def init_main(args):
  if os.path.exists(args.salts_file):
    raise FileExistsError(args.salts_file)
  else:
    pow.dump_salts(args.salts_file, {})

parser = argparse.ArgumentParser()
parser.set_defaults(main=None)

subparsers = parser.add_subparsers()

raw_parser = subparsers.add_parser('raw', help='just generate gobbledygook for a given string')
raw_parser.set_defaults(main=raw_main)
raw_parser.add_argument('-p', '--print', action='store_true')

add_parser = subparsers.add_parser('add', help='add a new salt')
add_parser.set_defaults(main=add_main)
add_parser.add_argument('-f', '--salts-file', default=os.path.join(os.environ['HOME'], '.salts.json'))

gob_parser = subparsers.add_parser('gob', help='compute gobbledygook using salt-file')
gob_parser.set_defaults(main=gob_main)
gob_parser.add_argument('-f', '--salts-file', default=os.path.join(os.environ['HOME'], '.salts.json'))
gob_parser.add_argument('--print', action='store_true')
gob_parser.add_argument('--persistent', action='store_true')
gob_parser.add_argument('query')

info_parser = subparsers.add_parser('info', help='print out salt-info')
info_parser.set_defaults(main=info_main)
info_parser.add_argument('-f', '--salts-file', default=os.path.join(os.environ['HOME'], '.salts.json'))
info_parser.add_argument('query')

init_parser = subparsers.add_parser('init', help='create a new salt-fil')
init_parser.set_defaults(main=init_main)
init_parser.add_argument('-f', '--salts-file', default=os.path.join(os.environ['HOME'], '.salts.json'))



if __name__ == '__main__':
  args = parser.parse_args()

  if args.main is None:
    parser.parse_args(['--help'])
  else:
    args.main(args)
