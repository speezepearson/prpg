import string

SHORTHANDS = {
  'a-z': string.ascii_lowercase,
  'A-Z': string.ascii_uppercase,
  '0-9': string.digits,
}

def chars_matching_charspec(spec):
  return SHORTHANDS.get(spec, spec)
