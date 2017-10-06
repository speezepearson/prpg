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

      try:
        k = determine_query_result(salts.keys(), query)
      except ValueError:
        print('no matches')
      else:
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


def _add_salts_file_argument(parser):
  parser.add_argument(
    '-f', '--salts-file',
    default=os.path.join(os.environ['HOME'], '.salts.json'),
    help='ROT13ed JSON file containing information about various applications (default ~/.salts.json)')
def _add_print_argument(parser):
  parser.add_argument(
    '-p', '--print', action='store_true',
    help='print output instead of copying to clipboard')
def _add_query_argument(parser):
  parser.add_argument('query', help='regular expression matching beginning of desired salt')

parser = argparse.ArgumentParser()
parser.set_defaults(main=None)
parser.add_argument('--no-self-test', action='store_false', dest='self_test', help='do not run self-tests at beginning')

subparsers = parser.add_subparsers()

raw_parser = subparsers.add_parser('raw', help='just generate gobbledygook for a given string')
raw_parser.set_defaults(main=raw_main)
_add_print_argument(raw_parser)

add_parser = subparsers.add_parser('add', help='add a new salt')
add_parser.set_defaults(main=add_main)
_add_salts_file_argument(add_parser)

gob_parser = subparsers.add_parser('gob', help='compute gobbledygook using salt-file')
gob_parser.set_defaults(main=gob_main)
_add_salts_file_argument(gob_parser)
_add_print_argument(gob_parser)
_add_query_argument(gob_parser)
gob_parser.add_argument('--persistent', action='store_true', help='continue running, rememberin seed and waiting for more queries')

info_parser = subparsers.add_parser('info', help='print out salt-info')
info_parser.set_defaults(main=info_main)
_add_salts_file_argument(info_parser)
_add_query_argument(info_parser)

init_parser = subparsers.add_parser('init', help='create a new salt-fil')
init_parser.set_defaults(main=init_main)
_add_salts_file_argument(init_parser)



if __name__ == '__main__':
  args = parser.parse_args()

  if args.self_test:
    test_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test.sh')
    if subprocess.call(['bash', test_file]) != 0:
      print(file=sys.stderr)
      print('tests failed; refusing to run', file=sys.stderr)
      exit(1)


  if args.main is None:
    parser.parse_args(['--help'])
  else:
    args.main(args)
