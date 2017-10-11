from . import add_salt_file_argument, add_mangle_master_argument, add_print_argument, add_query_argument, print_or_copy_and_notify
from .. import getseed
from ..saltfiles import load_salts, dump_salts, disambiguate, fuzzy_search, master_and_salt_and_saltinfo_to_password
from ..rot13 import rot13
from ..clipboard import copy_to_clipboard

def main(args):
  salts = load_salts(args.salt_file)

  query = args.query
  salt = disambiguate(fuzzy_search(salts, query))
  print('Chosen salt: {!r}'.format(salt))
  master = (getseed.get_mangled_seed() if args.mangle_master else getseed.get_seed())

  print_or_copy_and_notify(master_and_salt_and_saltinfo_to_password(master, salt, salts[salt]), should_print=args.print, message='Copied password for {!r} to clipboard.'.format(salt))

  if args.persistent:

    rot13_master = pow.rot13(master); del master

    while True:

      salts = load_salts(args.salt_file)
      print()
      query = input('Query: ')

      try:
        salt = disambiguate(fuzzy_search(salts, query))
      except ValueError:
        print('no matches')
      else:
        print_or_copy_and_notify(master_and_salt_and_saltinfo_to_password(rot13(rot13_master), salt, salts[salt]), should_print=args.print, message='Copied password for {!r} to clipboard.'.format(salt))


def prepare_parser(parser):
  add_mangle_master_argument(parser)
  add_salt_file_argument(parser)
  add_print_argument(parser)
  add_query_argument(parser)
  parser.add_argument('--persistent', action='store_true', help='continue running, remembering master password and waiting for more queries')

  parser.set_defaults(main=main)
