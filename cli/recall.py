from . import add_salt_file_argument, add_mangle_master_argument, add_print_argument, add_query_argument
from .. import getseed
from ..saltfiles import load_salts, dump_salts, disambiguate, fuzzy_search, master_and_salt_and_saltinfo_to_password
from ..rot13 import rot13
from ..clipboard import copy_to_clipboard

def main(args):
  salts = load_salts(args.salt_file)
  print_or_copy = (print if args.print else copy_to_clipboard)

  query = args.query
  salt = disambiguate(fuzzy_search(salts, query))
  master = (getseed.get_mangled_seed() if args.mangle_master else getseed.get_seed())

  print_or_copy(master_and_salt_and_saltinfo_to_password(master, salt, salts[salt]))

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
        result = master_and_salt_and_saltinfo_to_password(rot13(rot13_master), salt, salts[salt])
        print_or_copy(result)


def prepare_parser(parser):
  add_mangle_master_argument(parser)
  add_salt_file_argument(parser)
  add_print_argument(parser)
  add_query_argument(parser)
  parser.add_argument('--persistent', action='store_true', help='continue running, remembering master password and waiting for more queries')

  parser.set_defaults(main=main)
