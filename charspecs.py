import re

def chars_matching_charspec(spec):
  return ''.join(chr(i) for i in range(256) if re.match('['+spec+']', chr(i)))

assert chars_matching_charspec('a-z') == 'abcdefghijklmnopqrstuvwxyz'
assert chars_matching_charspec('0-9') == '0123456789'
assert chars_matching_charspec('!#$') == '!#$'
