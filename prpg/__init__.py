import json
import subprocess
import argparse
import sys

from .clipboard import copy_to_clipboard
from .rot13 import rot13
from .core import master_and_salt_to_password

from . import cli

def main():
  parser = argparse.ArgumentParser()
  cli.prepare_parser(parser)
  args = parser.parse_args()

  if hasattr(args, 'main'):
    try:
      args.main(args)
    except KeyboardInterrupt:
      print('Keyboard interrupt caught; exiting', file=sys.stderr)
      exit(1)
  else:
    parser.parse_args(['--help'])
