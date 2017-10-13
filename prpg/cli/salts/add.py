import json
import os
import sys
from ...saltfiles import load_salts, dump_salts, disambiguate, fuzzy_search

def main(args):
  if not os.path.exists(args.salt_file):
    print('Creating new salt-file in {!r}'.format(args.salt_file))
    dump_salts(args.salt_file, {})
  salts = load_salts(args.salt_file)
  if args.salt in salts:
    raise KeyError('salt {!r} already exists'.format(args.salt))
  salts[args.salt] = args.json
  dump_salts(args.salt_file, salts)

def prepare_parser(parser):
  parser.add_argument('salt')
  parser.add_argument('--json', type=json.loads, default={})
  parser.set_defaults(main=main)
