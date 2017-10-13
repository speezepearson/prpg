import sys
import string
import random
import getpass

def get_seed():
  return getpass.getpass('Master: ')

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
    print(file=sys.stderr)
    print('               '+charset, file=sys.stderr)
    print('Translates to: '+shuffled_charset, file=sys.stderr)
    c = getpass.getpass('Next translated character: ')
    if len(c) == 1:
      result += charset[shuffled_charset.index(c)]
    elif len(c) == 0:
      return result
    else:
      print('(looks like you entered multiple characters; try again)', file=sys.stderr)
