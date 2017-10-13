import sys

def rot13(s):
  return ''.join(
    chr(ord('a') + ((ord(c)+13-ord('a')) % 26)) if ord('a') <= ord(c) <= ord('z') else
    chr(ord('A') + ((ord(c)+13-ord('A')) % 26)) if ord('A') <= ord(c) <= ord('Z') else
    c
    for c in s)

if __name__ == '__main__':
  sys.stdout.write(rot13(sys.stdin.read()))
