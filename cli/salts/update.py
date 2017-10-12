import json
from ..common_args import add_query_argument
from ...saltfiles import load_salts, dump_salts, disambiguate, fuzzy_search

def main(args):
  salts = load_salts(args.salt_file)
  salt = disambiguate(fuzzy_search(salts, args.query))
  if input('Are you sure you want to update your salt for {!r}? [y/N] '.format(salt)) == 'y':
    salts[salt].update(args.json)
    dump_salts(args.salt_file, salts)

def prepare_parser(parser):
  add_query_argument(parser)
  parser.add_argument('json', type=json.loads)
  parser.set_defaults(main=main)
