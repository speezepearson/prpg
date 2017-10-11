import subprocess
import sys
import string
import random

def get_seed():
  result = subprocess.Popen(['/bin/bash', '-c', 'read -s -p "Master: " SEED && export SEED && env | sed -n -e "s/^SEED=//p"'], stdout=subprocess.PIPE).communicate()[0].decode().strip()
  if sys.stdout.isatty():
    print()
  return result

def get_mangled_seed():
  rng = random.Random()
  with open('/dev/random', 'rb') as f:
    rng.seed(f.read(64))
  charset = ''.join([string.ascii_lowercase, string.ascii_uppercase, string.digits, string.punctuation])

  print('Use these lookup tables to translate/enter your master password, one character at a time; enter nothing when you are done')

  result = ''
  while True:
    shuffled_charset = list(charset)
    rng.shuffle(shuffled_charset)
    shuffled_charset = ''.join(shuffled_charset)
    print()
    print(charset)
    print(shuffled_charset)
    entry = get_seed()
    if len(entry) == 1:
      result += charset[shuffled_charset.index(entry[0])]
    elif len(entry) == 0:
      return result
    else:
      print('(looks like you entered multiple characters; try again)')
