from . import add_mangle_master_argument, add_print_argument
from .. import getseed
from ..core import master_and_salt_to_password
from ..charsets import chars_matching_charspec
from ..clipboard import copy_to_clipboard

def main(args):
  print_or_copy = (print if args.print else copy_to_clipboard)
  master = (getseed.get_mangled_seed() if args.mangle_master else getseed.get_seed())

  charsets = [chars_matching_charspec(c) for c in args.charsets]

  print_or_copy(master_and_salt_to_password(master, args.salt, charsets))


def prepare_parser(parser):
  add_mangle_master_argument(parser)
  add_print_argument(parser)
  parser.add_argument('--salt', required=True)
  parser.add_argument('--charsets', nargs='+', required=True)
  parser.set_defaults(main=main)
