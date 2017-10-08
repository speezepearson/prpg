import subprocess
import json
import tempfile
import unittest
from string import ascii_lowercase as lower, ascii_uppercase as upper, digits

import pow


def call_gob(salts, args, seed):
  with tempfile.NamedTemporaryFile('w+') as f:
    f.write(pow.rot13(json.dumps(salts)))
    f.file.flush()

    command = ['python', '-m', 'pow', '--no-self-test',
               'gobble', '-f', f.name, '--print'] + args
    p = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    return p.communicate((seed+'\n').encode('utf-8'))[0].decode().strip()


class TestPow(unittest.TestCase):

  def test_core(self):
    self.assertEqual(
      pow.string_to_gobbledygook('foo', [lower, upper, digits, '!']),
      'wQ4!34PvMko0jV!jTLUVVCxIWkVT1THwWkmb5eY4htWid')
    self.assertEqual(
      pow.string_to_gobbledygook('foo bar', [lower, upper, digits, '!']),
      'rO8!Kwi7K5uzEE21icnpewdKHVjGIf0bvUkXgod3WVR4r')

  def test_gob__fuzzy_match(self):
    self.assertEqual(call_gob(salts={'bar': {}}, args=['b'], seed='foo'), 'rO8!Kwi7K5uzEE21')

  def test_gob__respects_length(self):
    self.assertEqual(call_gob(salts={"bar": {"length": 8}}, args=['b'], seed='foo'), 'rO8!Kwi7')

  def test_gob__respects_charsets(self):
    self.assertEqual(call_gob(salts={"bar": {"charset_specs": ["a-z", "A-Z", "0-9"]}}, args=['b'], seed='foo'), 'rO8TxkGI23Zv9Itd')

  def test_gob__respects_postprocessor(self):
    self.assertEqual(call_gob(salts={"bar": {"postprocess": "lambda g: g[1:16]"}}, args=['b'], seed='foo'), 'O8!Kwi7K5uzEE21')

  def test_gob__respects_salt(self):
    self.assertEqual(call_gob(salts={"bar": {"salt": "bar.com"}}, args=['b'], seed='foo'), 'wH7!7dEwY0r!2wZb')

unittest.main()
