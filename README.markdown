A very simple, very safe password manager.

This package views a password as a digital signature: in a sense, you use your master password to sign the string "example.com" (or whatever you like), to get a string that fulfills the site's password requirements.

Reasons to use this scheme:

- You only have to remember one password.
- Your passwords are not stored anywhere, not even encrypted. It is impossible __even in principle__ for somebody to steal them out of this password manager, unless they have your master password (in which case you're obviously hosed) or they crack HMAC-SHA256 (in which case we all are).
- The algorithm is simple enough that you could re-implement it yourself (if you're fairly computer-and-crypto-savvy; if not, hopefully one of your friends is). You don't need to trust me. You are not reliant on me. If you lose access to this package, or stop trusting it, or something, you can re-implement the scheme on your own in under ten minutes and recover all your passwords.


Example Usage
-------------

Basic, standalone usage:

```bash
~ $ python -m pow compute --salt 'example.com:username' --charsets a-z A-Z 0-9 '!'
Master: ********
Copied password for 'example.com:username' to clipboard.
~ $
```

But it's a hassle to type all that every time. Pow can maintain a list of salts that you can easily fuzzy-search by prefix:

```bash
~ $ alias addsalt='python -m pow salts add'
~ $ alias pow='python -m pow recall'
~ $
~ $ # set up a new salt, once
~ $ addsalt 'example.com:username'
Creating new salt-file in '/home/spencer/.pow-salts.json'
~ $ rot13 < ~/.pow-salts.json
{
  "example.com:username": {}
}
~ $
~ $ # compute your password
~ $ pow ex
Chosen salt: 'example.com:username'
Master:
Copied password for 'example.com:username' to clipboard.
~ $
```

(The salt-file is ROT13-encrypted by default, as a weak protection against somebody grepping your computer for bank-related words.)

Some sites have dumb password requirements. Pow's default charsets are `['a-z', 'A-Z', '0-9', '!']`, and the default postprocessing step is to trim the password to 16 characters -- but these can both be customized, by storing a JSON object alongside the salt:
```bash
~ $ addsalt 'we-disallow-punctuation.com:speeze' --json '{"charsets": ["a-z", "A-Z", "0-9"]}'
~ $ addsalt 'stupid-short-max-password-length.com:spencer' --json '{"postprocess": "lambda pw: pw[-12:]"}'
~ $
~ $ pow we --print
Chosen salt: 'we-disallow-punctuation.com:speeze'
Master:
dIfO89ZhvH07qbG3
~ $ pow stu --print
Chosen salt: 'stupid-short-max-password-length.com:spencer'
Master:
mu8AaBgRzD2!
~ $
```
You can also just store random not-very-sensitive information you want to associate with the salt:

```bash
$ addsalt 'blub.com:mylogin' --json '{"email address": "nobody@invalid.com", "birthday": "1970-01-01"'
$ python -m pow info bl
Chose: blub.com:mylogin
{
  "email address": "nobody@invalid.com",
  "birthday": "1970-01-01"
}
```




The Algorithm
-------------

Read this section if you want to be able to re-implement this module in times of need. One of my design goals has been to make the algorithm as memorable as possible, while staying cryptographically respectable and suitable for most/all password purposes.

tldr: using the most natural algorithm for each step: turn your master password into a key; use the key to sign the empty string; interpret that signature as a number; and express it in the base defined by the required character sets (by default `['a-z', 'A-Z', '0-9', '!']`), and truncate that to a good password-length, starting from the entropy-denser end.

The most natural...

- ...__signature algorithm__ is HMAC-SHA256;
- ...__key derivation algorithm__ is PBKDF2, with a million iterations (and using HMAC-SHA256 as a PRF, naturally);
- ...__signature-to-number algorithm__ is to interpret the hex-digest as a hexadecimal number;
- ...__base corresponding to a bunch of charsets__ is where the last digit is drawn from the last charset, the second-to-last digit from the second-to-last charset, etc., until you run out of charsets; further digits are drawn from the union of all charsets;
- ...__password length__ is 16. (The right-hand end is the entropy-denser one; careful thought will reveal that the most significant digit is not entirely random.)


### As Code

Here is the complete algorithm:

```python
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

def master_and_salt_to_password(master: str, salt: str, charsets) -> str:
  key = hashlib.pbkdf2_hmac(
          hash_name='sha256',
          password=master.encode('utf-8'),
          salt=salt.encode('utf-8'),
          iterations=10**6)
  mac = hmac.new(key=key, msg=b'', digestmod=hashlib.sha256)
  n = int(mac.hexdigest(), 16)
  return number_to_password(n, charsets)
```


### Background: Mixed-Radix Systems

tldr: expressing a number "in base (...)(abcde)(fgh)(ijkl)" means the last digit is in base 4, where i=0, j=1, k=2, l=3; the next digit is in base 3, where f=0, g=1, h=2; and all other digits are in base 5, where a=0, ..., e=4. So in that base, "ecbfk" represents the number (4*300 + 2*60 + 1*12 + 0*4 + 3 = 1335).

Recall that on a microwave, "1:23" means there are 83 seconds left, because the middle digit only goes up to 5.

So, we can say that "123" is "83 expressed in base (...)(0-9)(0-5)(0-9)." The possible characters we can put in the rightmost place are ["0", "1", ..., "9"]; for the second-rightmost, ["0", "1", ..., "5"]; for the third-rightmost and all others, 0-9 again.

To express 83 in base (...)(0-9)(0-5)(0-9):

- We first find the rightmost digit: there are 10 possibilities, so we take [83 mod 10 = 3] and that's the last digit.
- To compute the rest of the digits, we take the quotient (i.e. floor(83/10)) and express it in base (...)(0-9)(0-5) (which we got by dropping the rightmost place of the old base). The quotient is 8.
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

1. Use PBKDF2-HMAC-SHA256 to convert the master password, salted with the purpose, with 10^5 iterations, into a key.
2. Use that key to sign the empty string, using HMAC-SHA256, to obtain a 64-character hex string.
3. Interpret that as a (gigantic) hexadecimal number, and write it in a particular mixed-radix system (described below) derived from the given charsets. The result is a string that contains at least one character from each charset.

If the required charsets are `['a-z', 'A-Z', '0-9', '!']` (Pow's default), we define the corresponding numeral system to be `(...)(a-zA-Z0-9!)(a-z)(A-Z)(0-9)(!)`

That is: the last digit is drawn from the last charset; the second-to-last from the second-to-last; etc.; until there are no more charsets, and then all remaining digits are drawn from the concatenation of all the charsets.


Hand-Worked Example
-------------------

- Get the MAC (not by hand):

    ```python
    key = pbkdf2_hmac(password=master_password, salt="github.com:speezepearson", iterations=10**5, hash_function=sha256)
    mac = hmac_sha256(key=key, msg="").hexdigest()
    ```

- Suppose the MAC is `000...000864c6` (implausibly small, for the sake of example). Interpreted as a hex number, this equals 550086. Let's express this using the charsets `['a-z', '0-9']`.
- The corresponding base is `(...)(a-z0-9)(a-z)(0-9)`.
- 550086 mod 10 =  6 (quotient 55008); `'0123456789'[6]  = '6'`
-  55008 mod 26 = 18 (quotient  2115); `'abcd...xyz'[18] = 's'`
-   2115 mod 36 = 27 (quotient    58); `'a...z0...9'[27] = '1'`
-     58 mod 36 = 22 (quotient     1); `'a...z0...9'[22] = 'w'`
-      1 mod 36 =  1 (quotient     0); `'a...z0...9]'[1] = 'b'`
- We've reached 0. We're done. The result is 'bw1s6'.
