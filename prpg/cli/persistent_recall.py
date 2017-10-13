import itertools
import sys

from . import print_or_copy_and_notify
from .askpass import askpass
from .common_args import (
  add_mangle_master_argument,
  add_salt_file_argument,
  add_print_argument)
from ..saltfiles import (
  load_salts,
  disambiguate,
  fuzzy_search,
  master_and_salt_and_saltinfo_to_password)
from ..rot13 import rot13

def forever(f):
  while True:
    yield f()

def main(args):

  # HYPERPARANOIA: store the master ROT13ed in case somebody
  # snoops through our process memory or something crazy like that.
  rot13_master = rot13(askpass(mangle=args.mangle_master))

  while True:
    query = input('Query: ')

    salts = load_salts(args.salt_file)
    try:
      salt = disambiguate(fuzzy_search(salts, query))
    except ValueError:
      print('no matches', file=sys.stderr)
    else:
      print('Chosen salt: {!r}'.format(salt), file=sys.stderr)
      print_or_copy_and_notify(
        master_and_salt_and_saltinfo_to_password(rot13(rot13_master), salt, salts[salt]),
        should_print=args.print,
        message='Copied password for {!r} to clipboard.'.format(salt))

    print(file=sys.stderr)


def prepare_parser(parser):
  add_mangle_master_argument(parser)
  add_salt_file_argument(parser)
  add_print_argument(parser)

  parser.set_defaults(main=main)
