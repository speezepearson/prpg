#!/usr/bin/python3

import argparse
import os
import sys
from ..clipboard import copy_to_clipboard

def print_or_copy_and_notify(s: str, should_print: bool, message:str = ''):
  if should_print:
    print(s)
  else:
    copy_to_clipboard(s)
    print(message, file=sys.stderr)

def prepare_parser(parser):
  subparsers = parser.add_subparsers()

  compute_parser = subparsers.add_parser('compute', help='just compute a password')
  compute.prepare_parser(compute_parser)

  salts_parser = subparsers.add_parser('salts', help='view/edit a salt-file')
  salts.prepare_parser(salts_parser)

  recall_parser = subparsers.add_parser('recall', help='quickly recall a password using your salt-file')
  recall.prepare_parser(recall_parser)

  persistent_recall_parser = subparsers.add_parser('persistent-recall', help='recall many passwords using your salt-file, typing your master only once')
  persistent_recall.prepare_parser(persistent_recall_parser)


from . import compute
from . import salts
from . import recall
from . import persistent_recall
