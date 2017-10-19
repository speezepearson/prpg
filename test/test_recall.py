import tempfile
import contextlib
import shlex
import os
import pexpect

import pytest

import prpg

from . import spawn_prpg, expect_exact_line


@contextlib.contextmanager
def temp_salts(salts):
  with tempfile.NamedTemporaryFile('w+') as f:
    prpg.saltfiles.dump_salts(f.name, salts)
    yield f.name

@contextlib.contextmanager
def spawn_recall(salts, args):
  with temp_salts(salts) as salt_path:
    p = spawn_prpg('recall --print --salt-file '+shlex.quote(salt_path)+' '+args)
    yield p


def test_fails_when_no_salt_file():
  nonexistent_file = tempfile.mktemp()
  p = spawn_prpg('recall --salt-file '+shlex.quote(nonexistent_file)+' query')
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
    expect_exact_line(p, 'CUbe1hi1tC/BsOGfAa0+')
    p.expect(pexpect.EOF)

def test_disambiguates_ambiguous_query():
  for (choice, output) in [('1', r'CUbe1hi1tC/BsOGfAa0+'), ('2', r'6QK2fN3zFNLFyLYBAa0+')]:
    with spawn_recall(salts={'bar': {}, 'baz': {}}, args='b') as p:
      p.expect(r'Choose an option:', timeout=1)
      p.sendline(choice)
      p.expect(r'Master: ', timeout=1)
      p.sendline('foo')
      expect_exact_line(p, output)
      p.expect(pexpect.EOF)


def test_respects_salt():
  with spawn_recall(salts={'bar': {'__salt__': 'baz'}}, args='b') as p:
    import sys; p.logfile = sys.stdout
    p.expect(r'Master: ', timeout=1)
    p.sendline('foo')
    expect_exact_line(p, '6QK2fN3zFNLFyLYBAa0+')
    p.expect(pexpect.EOF)

def test_respects_postprocess():
  with spawn_recall(salts={'bar': {'__postprocess__': 'lambda s: s'}}, args='b') as p:
    import sys; p.logfile = sys.stdout
    p.expect(r'Master: ', timeout=1)
    p.sendline('foo')
    expect_exact_line(p, 'CUbe1hi1tC/BsOGfc/2dZpL/sl2VLKYM/B3GRUEKSpE=')
    p.expect(pexpect.EOF)
