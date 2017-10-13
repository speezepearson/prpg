A very simple, very safe password manager.

This package views a password as a sort of digital signature: in a sense, you use your master password to sign the string "example.com" (or whatever you like), resulting in a string that fulfills the site's password requirements.

Reasons to use this scheme:

- As with other password managers, you only have to remember one password.
- Unlike other password managers, your passwords are not stored anywhere, not even encrypted. It is impossible __even in principle__ for somebody to steal them out of this password manager, unless they have your master password (in which case you're obviously doomed) or they crack SHA256 and PBKDF2 (in which case we all are).
- Kinda like other password managers, you can easily get your passwords on a foreign computer. Just `pip install prpg && prpg compute example.com:username`. (Well... as with other password managers, typing your master password into a foreign computer is a terrible idea. But you may be interested in the `--mangle-master` command-line option, which, at the cost of some tedious manual work, lets you enter your master password in a way that ensures it can't be recovered from a screenscraper/keylogger (though both together could recover it).)
- Unlike other password managers, the algorithm is simple enough that you could re-implement it yourself (if you're fairly computer-and-crypto-savvy; if not, hopefully one of your friends is). You don't need to trust me. You are not reliant on me. If you lose access to this package, or stop trusting it, or something, you can re-implement the scheme on your own in under ten minutes and recover all your passwords.

Reasons to not use this scheme:

- Because it doesn't store passwords, you can't store your pre-existing passwords.
- If somebody steals your master password, they can rederive all your passwords. Other password managers kinda have this problem, but they at least require that the Bad Guy steal your vault-file too. Unless the password manager is cloud-based, in which case you're super doomed.
- The passwords this produces are hard to type and harder to remember. Copy-paste is the only way you'll find this useful.


Example Usage
-------------

(First, install, with `pip install prpg`.)

Basic, standalone usage:

```bash
~ $ prpg compute 'example.com:username'
Master: ********
Copied password for 'example.com:username' to clipboard.
~ $
```

By default, this generates a 16-character password with all the major kinds of character (lower, upper, digit, punctuation) -- but this is customizable.

But with this usage, you have to remember all your salts -- and remember them _exactly_ -- and type them in each time. What a hassle!

For this reason, PRPG can maintain a list of salts that it can easily fuzzy-search by prefix:

```bash
~ $ alias addsalt='prpg salts add'
~ $ alias pw='prpg recall'
~ $
~ $ # set up a new salt, once
~ $ addsalt 'example.com:username'
Creating new salt-file in '/home/spencer/.prpg-salts.json'
~ $ rot13 < ~/.prpg-salts.json
{
  "example.com:username": {}
}
~ $
~ $ # compute your password
~ $ pw ex
Chosen salt: 'example.com:username'
Master: ********
Copied password for 'example.com:username' to clipboard.
~ $
```

(The salt-file is ROT13-encrypted by default, as a weak protection against somebody grepping your computer for bank-related words. Yes, I _know_ that security through obscurity is frowned upon, but-- hey, it kinda works if you _stay_ obscure. Which I expect this package to do.)

(Also, there's nothing special about the format `sitename.com:myusername`! The salts can be anything you want.)

Each salt has a JSON object associated with it, which you can view using `prpg salts get SALTNAME`. You can store arbitrary random insensitive information in this object:

```bash
~ $ addsalt 'blub.com:mylogin' --json '{"email address": "nobody@invalid.com", "birthday": "1970-01-01"}'
~ $ prpg salts get bl
{'birthday': '1970-01-01', 'email address': 'nobody@invalid.com'}
```

There are also three special keys that object can have:

- `charsets` governs which characters may-and-must appear in the password:

    ```bash
    ~ $ addsalt 'we-disallow-punctuation.com:speeze' --json '{"charsets": ["a-z", "A-Z", "0-9"]}'
    ~ $ prpg we --print
    Chosen salt: 'we-disallow-punctuation.com:speeze'
    Master: ********
    dIfO89ZhvH07qbG3
    ~ $
    ```

- `postprocess` lets you write an arbitrary transformation on the password, using a Python lambda:

    ```bash
    ~ $ addsalt 'stupid-short-max-password-length.com:spencer' --json '{"postprocess": "lambda pw: pw[-12:]"}'
    ~ $ prpg stu --print
    Chosen salt: 'stupid-short-max-password-length.com:spencer'
    Master: ********
    mu8AaBgRzD2!
    ~ $
    ```

    If you try to use this feature, you may be perplexed by the fact that the string passed into the `postprocess` function is much longer than 16 characters: that's because it contains the full 32 bytes of entropy output by SHA-256, and the default `postprocess` function just trims it to 16 characters.

- `salt` tells PRPG, "I know this salt is named `example.com:username`, but I you should salt my master password with this other string instead." This might be useful if, say, a site changes its domain name.

    ```bash
    ~ $ prpg salts add 'blub-two-point-oh.com:mylogin' --json '{"salt": "blub.com:mylogin"}'
    ~ $ prpg recall blub.com --print
    Chosen salt: 'blub.com:mylogin'
    Master: ********
    D2YuMBK3qcVEdA3!
    ~ $ prpg recall blub-two --print
    Chosen salt: 'blub-two-point-oh.com:mylogin'
    Master: ********
    D2YuMBK3qcVEdA3!
    ```

For more information about bells and whistles, consider running `prpg --help`.


The Algorithm
-------------

Read this section if you want to be able to re-implement this module in times of need. One of my design goals has been to make the algorithm as memorable as possible, while staying cryptographically respectable and suitable for most/all password purposes.

tldr: interpret sha256(pbkdf2_hmac_sha256(master, salt, iterations=10**6)) as a huge hexadecimal number; express that number in the most natural numeral system defined by the required character sets; and truncate that to 16 characters.

Details:

The most natural numeral system corresponding to a bunch of charsets is a mixed-radix system where the last digit is drawn from the last charset, the second-to-last digit from the second-to-last charset, etc., until you run out of charsets; further digits are drawn from the union of all charsets. The default character sets are `['a-z', 'A-Z', '0-9', '!']`. (My mnemonic is "the four major classes of character, ordered by how often I use them; punctuation is represented by `!` alone, because I'm excited about passwords.")

(You might think that it's more natural to say that the _first_ digit should come from the _first_ charset, etc., but that's provably bad: careful thought will reveal that the _first_ digit, i.e. the _most significant_ one, won't be completely random.)

The truncation starts from the right-hand end of the number, because that's the end that's guaranteed to have characters from all the required character sets.


### As Code

Here is the complete algorithm:

```python
import hashlib

def number_to_password(n: int, charsets: Sequence[str]) -> str:
  result = ''
  for charset in reversed(charsets):
    (n, i) = divmod(n, len(charset))
    result = charset[i] + result
  charset = ''.join(charsets)
  while n > 0:
    (n, i) = divmod(n, len(charset))
    result = charset[i] + result
  return result

def master_and_salt_to_password(master: str, salt: str, charsets: Sequence[str]) -> str:
  key = hashlib.pbkdf2_hmac(
          hash_name='sha256',
          password=master.encode('utf-8'),
          salt=salt.encode('utf-8'),
          iterations=10**6)
  sha = hashlib.sha256(key).hexdigest()
  n = int(sha, 16)
  return number_to_password(n, charsets)
```


### Background: Mixed-Radix Systems

tldr: expressing a number "in base `(...)(abcde)(fgh)(ijkl)`" means the last digit is in base 4, where i=0, j=1, k=2, l=3; the next digit is in base 3, where f=0, g=1, h=2; and all other digits are in base 5, where a=0, ..., e=4. So in that base, "ecbfk" represents the number `4*300 + 2*60 + 1*12 + 0*4 + 3 = 1335`.

Recall that on a microwave, "1:23" means there are 83 seconds left, because the middle digit only goes up to 5.

So, we can say that "123" is "83 expressed in base `(...)(0-9)(0-5)(0-9)`." The possible characters we can put in the rightmost place are ["0", "1", ..., "9"]; for the second-rightmost, ["0", "1", ..., "5"]; for the third-rightmost and all others, 0-9 again.

To express 83 in base `(...)(0-9)(0-5)(0-9)`:

- We first find the rightmost digit: there are 10 possibilities, so we take [83 mod 10 = 3] and that's the last digit.
- To compute the rest of the digits, we take the quotient (i.e. floor(83/10) - 8) and express it in base `(...)(0-9)(0-5)` (which we got by dropping the rightmost place of the old base).
- [8 mod 6 = 2], so the next digit is 2; quotient 1.
- [1 mod 10 = 1], so the next digit is 1; quotient 0.
- We've reached 0, so we're done. The final answer is "123", as expected.

Explained more precisely
----------------------------------

Inputs:

- master password (string)
- purpose/application/site/username/whatever (string)
- an ordered list of "required charsets", e.g. ["a-z", "A-Z", "0-9", "!"]

The core algorithm here is a three-step process.

1. Use PBKDF2-HMAC-SHA256 to convert the master password, salted with the purpose, with a million iterations, into a key.
2. Hash that key, using HMAC-SHA256, to obtain a 64-character hex string.
3. Interpret that as a (gigantic) hexadecimal number, and write it in a particular mixed-radix system (described below) derived from the given charsets. The result is a string that contains at least one character from each charset.

If the required charsets are `['a-z', 'A-Z', '0-9', '!']` (PRPG's default), we define the corresponding numeral system to be `(...)(a-zA-Z0-9!)(a-z)(A-Z)(0-9)(!)`

That is: the last digit is drawn from the last charset; the second-to-last from the second-to-last; etc.; until there are no more charsets, and then all remaining digits are drawn from the concatenation of all the charsets.


Hand-Worked Example
-------------------

- Get the MAC (not by hand):

    ```python
    key = pbkdf2_hmac(password=master_password, salt="github.com:speezepearson", iterations=10**6, hash_function=sha256)
    mac = hmac_sha256(key=key, msg="").hexdigest()
    ```

- Suppose the MAC is `000...000864c6` (implausibly small, for the sake of example). Interpreted as a hex number, this equals 550086. Let's express this using the charsets `['a-z', '0-9']`.
- The corresponding base is `(...)(a-z0-9)(a-z)(0-9)`.
- 550086 mod 10 =  6 (quotient 55008); `'0123456789'[6]  = '6'`
- 55008 mod 26 = 18 (quotient  2115); `'abcd...xyz'[18] = 's'`
- 2115 mod 36 = 27 (quotient 58); `'a...z0...9'[27] = '1'`
- 58 mod 36 = 22 (quotient 1); `'a...z0...9'[22] = 'w'`
- 1 mod 36 =  1 (quotient 0); `'a...z0...9]'[1] = 'b'`
- We've reached 0. We're done. The result is 'bw1s6'.
