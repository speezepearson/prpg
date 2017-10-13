import re

import pexpect

from . import spawn_prpg

def expect_compute_result(options, password, expected):
  p = spawn_prpg('compute --print '+options)
  p.expect(r'Master: ', timeout=1)
  p.sendline(password)
  p.expect('\n'+re.escape(expected)+'\r?\n', timeout=3)
  p.expect(pexpect.EOF)

def test_basic():
  expect_compute_result('bar', password='foo', expected='JdS3dpz4li4rjD7!')

def test_respects_postprocessing():
  expect_compute_result('bar --charsets a-z 0-9 --postprocess "lambda s: s.upper()[-8:]"', password='foo', expected='IE8TWTD7')

def test_respects_charsets():
  expect_compute_result('bar --charsets a-z 0-9', password='foo', expected='tsij6nvsie8twtd7')

def test_respects_confirmation():
  p = spawn_prpg('compute --print --confirm bar')
  import sys; p.logfile=sys.stdout
  p.expect(r'Master: ', timeout=1)
  p.sendline('foo')
  p.expect(r'Confirm: ', timeout=1)
  p.sendline('foo')
  p.expect('\nJdS3dpz4li4rjD7!\r?\n', timeout=3)
  p.expect(pexpect.EOF)

  p = spawn_prpg('compute --print --confirm bar')
  p.expect(r'Master: ', timeout=1)
  p.sendline('foo')
  p.expect(r'Confirm: ', timeout=1)
  p.sendline('WRONG')
  p.expect(r'Passwords do not match. Try again.', timeout=1)
  p.expect(r'Master: ', timeout=1)
  p.sendline('foo')
  p.expect(r'Confirm: ', timeout=1)
  p.sendline('foo')
  p.expect('\nJdS3dpz4li4rjD7!\r?\n', timeout=3)
  p.expect(pexpect.EOF)

def test_respects_mangling():
  p = spawn_prpg('compute --print --mangle-master bar')

  for char in 'foo':
    p.expect(r' +(abc[^\n]*)\r?\n', timeout=1)
    chars = p.match.group().decode('utf-8')
    p.expect(r'Translates to: (.*)\r?\n', timeout=1)
    shuffled_chars = p.match.group().decode('utf-8')
    p.expect(r'Next translated character:', timeout=1)
    p.sendline(shuffled_chars[chars.index(char)])

  p.expect(r'Next translated character:', timeout=1)
  p.sendline('')

  p.expect(r'\nJdS3dpz4li4rjD7!\r?\n', timeout=3)
  p.expect(pexpect.EOF)
