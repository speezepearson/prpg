from . import print_or_copy_and_notify
from .askpass import askpass
from .common_args import add_mangle_master_argument, add_print_argument, add_confirm_argument
from ..saltfiles import master_and_salt_and_saltinfo_to_password
from ..clipboard import copy_to_clipboard

def main(args):
  print_or_copy = (print if args.print else copy_to_clipboard)
  master = askpass(mangle=args.mangle_master, confirm=args.confirm)

  salt_info = {}
  if args.salt is not None:
    salt_info['__salt__'] = args.salt
  if args.postprocess is not None:
    salt_info['__postprocess__'] = args.postprocess

  print_or_copy_and_notify(master_and_salt_and_saltinfo_to_password(master, args.salt, salt_info), should_print=args.print, message='Copied password for {!r} to clipboard.'.format(args.salt))


def prepare_parser(parser):
  add_mangle_master_argument(parser)
  add_print_argument(parser)
  add_confirm_argument(parser)
  parser.add_argument('salt')
  parser.add_argument('--postprocess')
  parser.set_defaults(main=main)
