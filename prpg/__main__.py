#!/usr/bin/python3

import argparse
import sys
import prpg

parser = argparse.ArgumentParser()
prpg.cli.prepare_parser(parser)
args = parser.parse_args()

if hasattr(args, 'main'):
  try:
    args.main(args)
  except KeyboardInterrupt:
    print('Keyboard interrupt caught; exiting', file=sys.stderr)
    exit(1)
else:
  parser.parse_args(['--help'])
