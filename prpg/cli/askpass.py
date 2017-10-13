import sys
import string
import random
import getpass

def askpass(prompt='Master: ', mangle=False, confirm=False):
  ask = (get_mangled_pass if mangle else getpass.getpass)

  result = ask(prompt=prompt)
  if confirm:
    confirmation = ask(prompt='Confirm: ')
    while result != confirmation:
      print('Passwords do not match. Try again.')
      result = ask(prompt=prompt)
      confirmation = ask(prompt='Confirm: ')

  return result

_DEFAULT_MANGLED_PROMPT = 'Use these lookup tables to translate/enter your master password, one character at a time; enter nothing when you are done'

def get_mangled_pass(prompt=_DEFAULT_MANGLED_PROMPT):
  rng = random.Random()
  with open('/dev/random', 'rb') as f:
    rng.seed(f.read(64))
  charset = ''.join([string.ascii_lowercase, string.ascii_uppercase, string.digits, string.punctuation])

  print(prompt, file=sys.stderr)

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
