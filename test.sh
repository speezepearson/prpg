#!/bin/bash

HERE=$(python -c 'import os, sys; print(os.path.dirname(os.path.realpath(sys.argv[1])))' "${BASH_SOURCE[0]}")
Red=$'\e[0;31m'          # Red
Color_Off=$'\e[0m'       # Text Reset

# Canonical implementation:
#   $ echo -n bar | shasum -a 256
#   fcde2b2edba56bf408601fb721fe9b5c338d10ee429ea04fae5511b68fbf8fb9  -
#   $ python
#   Python 3.6.1 (default, Mar 22 2017, 06:17:05)
#   [GCC 6.3.0 20170321] on linux
#   Type "help", "copyright", "credits" or "license" for more information.
#   >>> n = 0xfcde2b2edba56bf408601fb721fe9b5c338d10ee429ea04fae5511b68fbf8fb9
#   >>> import string
#   >>> charsets = [string.ascii_lowercase, string.ascii_uppercase, string.digits, '!']
#   >>> result = ''
#   >>> for cs in charsets: (result, n) = (result+cs[n%len(cs)], n//len(cs))
#   ...
#   >>> cs = ''.join(charsets)
#   >>> while n>0: (result, n) = (result+cs[n%len(cs)], n//len(cs))
#   ...
#   >>> result
#   'bA8!Kg7Np6mfvs2AFGbdWl6dxTvzdMxebD9NUQoCSxQ9r'
#   >>>

error-if-different() {
  EXPECTED=$1
  ACTUAL=$2
  MESSAGE=$3
  shift 2
  if [ "$EXPECTED" != "$ACTUAL" ]; then
    echo "${Red}FAILURE:${Color_Off} $*" >&2
    echo "  Expected: '$EXPECTED'" >&2
    echo "  Actual:   '$ACTUAL'" >&2
    echo "${Red}^^^ THIS TEST IS CORRECT BY DEFINITION; THE CODE IS WRONG.${Color_Off}" >&2
    return 1
  fi
  return 0
}

compare-raw() {
  SEED=$1
  EXPECTED=$2
  ACTUAL="$(echo "$SEED" | python "$HERE" raw --print)"
  error-if-different "$EXPECTED" "$ACTUAL" "raw gob of '$SEED' is wrong"
  return $?
}
if compare-raw 'foo' 'wrong answer' >/dev/null 2>&1; then
  echo "${Red}compare-raw does not alert about wrong answers!${Color_Off}" >&2
  echo "${Red}THIS IS REALLY BAD!${Color_Off}" >&2
fi

compare-salted-gob() {
  SEED=$1
  JSON=$2
  QUERY=$3
  EXPECTED=$4
  ACTUAL="$(echo "$SEED" | python "$HERE" gob "$QUERY" --print -f <(echo "$JSON" | rot13))"
  error-if-different "$EXPECTED" "$ACTUAL" "gob of $QUERY in $JSON, with seed $SEED, is wrong"
  return $?
}
if compare-salted-gob 'foo' '{"bar": {}}' 'b' 'wrong answer' >/dev/null 2>&1; then
  echo "${Red}compare-salted-gob does not alert about wrong answers!${Color_Off}" >&2
  echo "${Red}THIS IS REALLY BAD!${Color_Off}" >&2
fi


compare-raw 'foo' 'wQ4!34PvMko0jV!jTLUVVCxIWkVT1THwWkmb5eY4htWid'
compare-raw 'foo bar' 'rO8!Kwi7K5uzEE21icnpewdKHVjGIf0bvUkXgod3WVR4r'

compare-salted-gob 'foo' '{"bar": {}}' 'b' 'rO8!Kwi7K5uzEE21'
compare-salted-gob 'foo' '{"bar": {"length": 8}}' 'b' 'rO8!Kwi7'
compare-salted-gob 'foo' '{"bar": {"charset_specs": ["a-z", "A-Z", "0-9"]}}' 'b' 'rO8TxkGI23Zv9Itd'
compare-salted-gob 'foo' '{"bar": {"postprocess": "lambda x: x[1:16]"}}' 'b' 'O8!Kwi7K5uzEE21'
