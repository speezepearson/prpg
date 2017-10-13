import tempfile
import contextlib
import shlex
import os
import pexpect

import pytest

import pow

from . import spawn_pow


@contextlib.contextmanager
def temp_salts(salts):
  with tempfile.NamedTemporaryFile('w+') as f:
    pow.saltfiles.dump_salts(f.name, salts)
    yield f.name

@contextlib.contextmanager
def spawn_recall(salts, args):
  with temp_salts(salts) as salt_path:
    p = spawn_pow(f'recall --print --salt-file {shlex.quote(salt_path)} '+args)
    yield p


def test_fails_when_no_salt_file():
  nonexistent_file = tempfile.mktemp()
  p = spawn_pow(f'recall --salt-file {shlex.quote(nonexistent_file)} query')
  import sys; p.logfile = sys.stdout
  p.expect(r'FileNotFoundError:', timeout=1)

def test_fails_when_no_salt_matches_query():
  with spawn_recall(salts={'bar': {}}, args='q') as p:
    p.expect(r'ValueError: no matches', timeout=1)

def test_runs_fine_with_unambiguous_query():
  with spawn_recall(salts={'bar': {}}, args='b') as p:
    import sys; p.logfile = sys.stdout
    p.expect(r'Master: ', timeout=1)
    p.sendline('foo')
    p.expect(r'\nJdS3dpz4li4rjD7!\r?\n')
    p.expect(pexpect.EOF)

def test_disambiguates_ambiguous_query():
  for (choice, output) in [('1', 'JdS3dpz4li4rjD7!'), ('2', 'Ojc2oC!Z1avHfU0!')]:
    with spawn_recall(salts={'bar': {}, 'baz': {}}, args='b') as p:
      p.expect(r'Choose an option:', timeout=1)
      p.sendline(choice)
      p.expect(r'Master: ', timeout=1)
      p.sendline('foo')
      p.expect(r'\n'+output+r'\r?\n')
      p.expect(pexpect.EOF)
