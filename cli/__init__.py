#!/usr/bin/python3

import argparse
import os
from ..clipboard import copy_to_clipboard

def add_salt_file_argument(parser):
  parser.add_argument(
    '-f', '--salt-file',
    default=os.path.join(os.environ['HOME'], '.pow-salts.json'),
    help='ROT13ed JSON file containing information about various applications (default ~/.pow-salts.json)')

def add_mangle_master_argument(parser):
  parser.add_argument('--mangle-master', action='store_true', help='enter master password in a laborious, char-by-char-mangled way if you are worried about keyloggers')

def add_print_argument(parser):
  parser.add_argument(
    '--print', action='store_true',
    help='print output instead of copying to clipboard')

def add_query_argument(parser):
  parser.add_argument('query', help='regular expression matching beginning of desired salt')


def print_or_copy_and_notify(s: str, should_print: bool, message:str = ''):
  if should_print:
    print(s)
  else:
    copy_to_clipboard(s)
    print(message)




from . import compute
from . import salts
from . import recall



def prepare_parser(parser):
  subparsers = parser.add_subparsers()

  compute_parser = subparsers.add_parser('compute', help='just compute a password')
  compute.prepare_parser(compute_parser)

  salts_parser = subparsers.add_parser('salts', help='view/edit a salt-file')
  salts.prepare_parser(salts_parser)

  recall_parser = subparsers.add_parser('recall', help='quickly recall a password using your salt-file')
  recall.prepare_parser(recall_parser)

#
# import pprint
# import json
# import argparse
# import os
# import subprocess
# import re
# import sys
# import os
# import hashlib
# import string
#
# import pow
#
# def raw_main(args):
#   print_or_copy = (print if args.print else pow.copy_to_clipboard)
#   result = pow.string_to_gobbledygook(pow.get_seed(), [string.ascii_lowercase, string.ascii_uppercase, string.digits, '!'])
#   print_or_copy(result)
#
# def info_main(args):
#   salts = pow.load_salts(args.salt_file)
#   k = determine_query_result(salts.keys(), args.query)
#   pprint.pprint(salts[k])
#
# def gobble_main(args):
#   salts = pow.load_salts(args.salt_file)
#   print_or_copy = (print if args.print else pow.copy_to_clipboard)
#   k = determine_query_result(salts.keys(), args.query)
#   seed = pow.get_seed()
#   result = pow.seed_and_salt_to_gobbledygook(seed, k, salts[k])
#   print_or_copy(result)
#
#   if args.persistent:
#     rot13_seed = pow.rot13(seed); del seed
#     while True:
#       print()
#       query = input('Query: ')
#
#       try:
#         k = determine_query_result(salts.keys(), query)
#       except ValueError:
#         print('no matches')
#       else:
#         result = pow.seed_and_salt_to_gobbledygook(pow.rot13(rot13_seed), k, salts[k])
#         print_or_copy(result)
#
# def add_main(args):
#   salts = pow.load_salts(args.salt_file)
#   k = input('New key: ')
#   salt = json.loads(input('New salt: '))
#   salts[k] = salt
#   pow.dump_salts(args.salt_file, salts)
#
# def init_main(args):
#   if os.path.exists(args.salt_file):
#     raise FileExistsError(args.salt_file)
#   else:
#     pow.dump_salts(args.salt_file, {})
#
#
# def _add_salt_file_argument(parser):
#   parser.add_argument(
#     '-f', '--salts-file',
#     default=os.path.join(os.environ['HOME'], '.pow-suffixes.json'),
#     help='ROT13ed JSON file containing information about various applications (default ~/.pow-suffixes.json)')
# def _add_print_argument(parser):
#   parser.add_argument(
#     '-p', '--print', action='store_true',
#     help='print output instead of copying to clipboard')
#
# parser = argparse.ArgumentParser()
# parser.set_defaults(main=None)
# parser.add_argument('--no-self-test', action='store_false', dest='self_test', help='do not run self-tests at beginning')
#
# subparsers = parser.add_subparsers()
#
# core_parser = subparsers.add_parser('core', help='just generate a password')
# core_parser.set_defaults(main=core_main)
# _add_print_argument(core_parser)
#
# salts_parser = subparsers.add_parser('salts', help='')
#
# salts_subparser = salts_parser.add_subparsers()
# salts_add_parser = calts_subparsers.add_parser('add', help='add a new salt to your salt-file')
# salts_add_parser.set_defaults(main=add_main)
# _add_salt_file_argument(add_parser)
#
#
# gobble_parser = subparsers.add_parser('gobble', help='compute gobbledygook using salt-file')
# gobble_parser.set_defaults(main=gobble_main)
# _add_salt_file_argument(gobble_parser)
# _add_print_argument(gobble_parser)
# _add_query_argument(gobble_parser)
# gobble_parser.add_argument('--persistent', action='store_true', help='continue running, rememberin seed and waiting for more queries')
#
# info_parser = subparsers.add_parser('info', help='print out salt-info')
# info_parser.set_defaults(main=info_main)
# _add_salt_file_argument(info_parser)
# _add_query_argument(info_parser)
#
# init_parser = subparsers.add_parser('init', help='create a new salt-fil')
# init_parser.set_defaults(main=init_main)
# _add_salt_file_argument(init_parser)
#
#
#
# if __name__ == '__main__':
#   args = parser.parse_args()
#
#   if args.self_test:
#     p = subprocess.Popen(['python', '-m', 'pow.test'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#     (out, err) = p.communicate()
#     if p.returncode != 0:
#       print(err.decode('utf-8'))
#       print('\nSELF-TESTS FAILED -- refusing to continue\n', file=sys.stderr)
#       exit(1)
#
#
#   if args.main is None:
#     parser.parse_args(['--help'])
#   else:
#     try:
#       args.main(args)
#     except KeyboardInterrupt:
#       print('Keyboard interrupt caught; exiting')
#       exit(1)
#     except EOFError:
#       print('EOF caught; exiting')
#       exit(0)
