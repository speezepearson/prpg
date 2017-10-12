import sys

from . import print_or_copy_and_notify
from .common_args import (
  add_salt_file_argument,
  add_mangle_master_argument,
  add_print_argument,
  add_query_argument)
from .. import getseed
from ..saltfiles import (
  load_salts,
  disambiguate,
  fuzzy_search,
  master_and_salt_and_saltinfo_to_password)

def main(args):
  salts = load_salts(args.salt_file)
  salt = disambiguate(fuzzy_search(salts, args.query))
  print('Chosen salt: {!r}'.format(salt), file=sys.stderr)
  master = (getseed.get_mangled_seed() if args.mangle_master else getseed.get_seed())
  print_or_copy_and_notify(
    master_and_salt_and_saltinfo_to_password(master, salt, salts[salt]),
    should_print=args.print,
    message='Copied password for {!r} to clipboard.'.format(salt))


def prepare_parser(parser):
  add_mangle_master_argument(parser)
  add_salt_file_argument(parser)
  add_print_argument(parser)
  add_query_argument(parser)

  parser.set_defaults(main=main)
