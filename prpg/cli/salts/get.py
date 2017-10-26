from __future__ import print_function
import sys
import json
import pprint
from ..common_args import add_query_argument
from ...saltfiles import load_salts, disambiguate, fuzzy_search

def main(args):
  salts = load_salts(args.salt_file)
  salt = disambiguate(fuzzy_search(salts, args.query))
  print('Chosen salt: {!r}'.format(salt), file=sys.stderr)
  pprint.pprint(salts[salt])

def prepare_parser(parser):
  add_query_argument(parser)
  parser.set_defaults(main=main)
