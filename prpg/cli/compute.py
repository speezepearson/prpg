from . import print_or_copy_and_notify
from .common_args import add_mangle_master_argument, add_print_argument
from .. import getseed
from ..saltfiles import master_and_salt_and_saltinfo_to_password
from ..charsets import chars_matching_charspec
from ..clipboard import copy_to_clipboard

def main(args):
  print_or_copy = (print if args.print else copy_to_clipboard)
  master = (getseed.get_mangled_seed() if args.mangle_master else getseed.get_seed())

  salt_info = {key: getattr(args, key) for key in ['salt', 'charsets', 'postprocess'] if getattr(args, key) is not None}

  print_or_copy_and_notify(master_and_salt_and_saltinfo_to_password(master, args.salt, salt_info), should_print=args.print, message='Copied password for {!r} to clipboard.'.format(args.salt))


def prepare_parser(parser):
  add_mangle_master_argument(parser)
  add_print_argument(parser)
  parser.add_argument('salt')
  parser.add_argument('--charsets', nargs='+')
  parser.add_argument('--postprocess')
  parser.set_defaults(main=main)
