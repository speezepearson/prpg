from ..common_args import add_salt_file_argument
from . import get
from . import add
from . import update
from . import delete

def prepare_parser(parser):
  add_salt_file_argument(parser)

  subparsers = parser.add_subparsers()

  get_subparser = subparsers.add_parser('get', help='get info for an existing salt')
  get.prepare_parser(get_subparser)

  add_subparser = subparsers.add_parser('add', help='add a new salt')
  add.prepare_parser(add_subparser)

  update_subparser = subparsers.add_parser('update', help='update info for an existing salt')
  update.prepare_parser(update_subparser)

  delete_subparser = subparsers.add_parser('delete', help='delete a salt')
  delete.prepare_parser(delete_subparser)
