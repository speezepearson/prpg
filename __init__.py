'''A pseudorandom gobbledygook generator.

(This documentation is intentionally slightly abstract, for reasonably good reasons.)

At its core, this package just provides a one-way function which converts a "seed" string into an entropy-dense "gobbledygook" string that is guaranteed to have characters from multiple given character-sets (e.g. lowercase, uppercase, digits). It uses a conceptually simple algorithm that is trivial to re-implement if, for some reason, you need to gobble a seed-string on a foreign computer.

On top of that core algorithm, this package offers a command-line interface that enables you to remember a single seed, and from that, easily generate any number of application-specific gobbledygook strings, such that nobody can determine the seed, even knowing everything else.

(To facilitate this, you can store various salts in a JSON file on your computer, typically in .salts.json, e.g.

    {
      "blub": {"arbitrary key": "arbitrary value"},
      "snark": {"length": 8,
                "thereby changing the length to which the gobbledygook will be truncated": ""},
      "frazzle": {"postprocess": "lambda gob: gob.upper()",
                  "thereby performing some transformation on the output gobbledygook": ""},
      "whale": {"charset_specs": ["a-z", "A-Z", "0-9"],
                "thereby defining which characters will/must appear in the gobbledygook": ""}
    }

(For a little extra unclarity, the JSON file is stored rot13ed. Occasionally inconvenient, I know.)

To create a salt-file, the `init` and `add` commands are useful. To create a file with the (effective, rot13ed-on-disk) above contents,

        ~ $ alias p='python -m pow'
        ~ $ p init # creates a new salt-file in ~/.salts.json
        ~ $ p add
        New key: <here, type `blub`>
        New salt: <here, type `{"arbitrary key": "arbitrary value"}`>
        ~ $ # repeat for other key/values

To fuzzy-search for a salt and salt a seed with it, the `gob` command is useful.

        ~ $ p gob f
        Chose: frazzle
        Seed: <here, type your seed -- e.g. "myseed">
        ~ $ # "myseed frazzle" has been gobbled and copied to the clipboard




Below is a complete description of the core algorithm:

- Hash the string (using SHA-256).
- Interpret the output as a hexadecimal number, `n`.
- Imagine that each character-set is a list of "digits" in base `len(charset)`. We can express any number as a "decimal" string using the "digits" in the charset. For example, the number twelve expressed in base "012" (i.e. ternary) is "110"; expressed in base "abc", it is "bba".
- For each charset, express `n` in that base; lop off the last digit and append it to the result; what's left is the new `n`.
- Concatenate all the charsets, and express `n` in that base; top off the last digit and append it to the result; repeat until there is nothing left.

For example:

- Suppose the input string hashed to "000...00066c708" (for simplicity, we pick an unrealistically small number).
- Interpreted as hex, that is 6735624.
- Suppose our desired character sets are [a-z] and [0-9]
- Expressed in base "a...z", 6735624 becomes "otfym"; the first character of the result is "m", and the new n is "otfy" => 259062.
- Expressed in base "0...9", 259062 becomes "259062"; the next character of the result is "2", and the new n is 25906.
- Expressed in base "a...z0...9", 25906 becomes "t9w"; the next character of the result is "w", repeat and we get "9", repeat and we get "t".
- Therefore, the gobbled version of the input string is "m2w9t".

'''

import json
import subprocess

from .choose import infer_choice
from .charspecs import chars_matching_charspec
from .clipboard import copy_to_clipboard
from .getseed import get_seed
from .rot13 import rot13
from .core import string_to_gobbledygook

def seed_and_salt_to_gobbledygook(seed, salt_name, info):
  desired_length = info.get('length', 16)
  charset_specs = info.get('charset_specs', ['a-z', 'A-Z', '0-9', '!'])
  charsets = [chars_matching_charspec(spec) for spec in charset_specs]
  postprocess = eval(info['postprocess']) if 'postprocess' in info else (lambda gob: gob[:desired_length])
  salt = info.get('salt', salt_name)
  return postprocess(string_to_gobbledygook(seed + ' ' + salt, charsets))


def load_salts(f):
  if hasattr(f, 'read'):
    return json.loads(rot13(f.read()))
  else:
    with open(f) as true_f:
      return load_salts(true_f)
def dump_salts(f, salts):
  payload = rot13(json.dumps(salts, sort_keys=True, indent='  '))
  if hasattr(f, 'write'):
    f.write(payload)
  else:
    with open(f, 'w') as true_f:
      true_f.write(payload)
