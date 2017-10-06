import hashlib

def choose(xs, seed):
  return (xs[seed % len(xs)], seed // len(xs))

def int_to_gobbledygook(n, required_charsets):

  all_valid_chars = ''.join(required_charsets)

  result = ''
  for charset in required_charsets:
    (c, n) = choose(charset, n)
    result += c

  while n > 0:
    (c, n) = choose(all_valid_chars, n)
    result += c

  return result

def string_to_gobbledygook(s, required_charsets):
  sha = hashlib.sha256(s.encode()).hexdigest()
  n = int(sha, 16)
  return int_to_gobbledygook(n, required_charsets)

assert choose('abcdefghijklmnopqrstuvwxyz', 25) == ('z', 0)
assert choose('abcdefghijklmnopqrstuvwxyz', 7*26 + 4) == ('e', 7)
