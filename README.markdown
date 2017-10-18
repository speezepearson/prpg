A one-line password manager.

`base64(sha256(pbkdf2_hmac('sha256', master, salt=site+username, iterations=1_000_000)))[:16]+'Aa0+'`

## Table of Contents
- [Summary](#summary)
- [Why is this good?](#why-is-this-good)
- [Why is this bad?](#why-is-this-bad)
- [Installation/Usage](#installationusage)
- [Internals/Reimplemenation](#internalsreimplementation)

## Summary
The big idea: you have a master password. All your other passwords are, effectively, digital signatures: strings that are easy to produce for somebody who knows the master password, but prohibitively difficult to compute for somebody who doesn't.

It turns out that this is jaw-droppingly simple to implement:

![diagram](diagram.png)

In effect, this is a cryptographically secure pseudo-random password generator (hence the name, PRPG): a deterministic algorithm that maps seeds (i.e. [master, site] pairs) to passwords, in such a way that no number of [input, output] pairs will give you information about the outputs corresponding to any other inputs.


## Why is this good?

- As with other password managers, you only have to remember one password.
- Unlike other password managers, your passwords are not stored anywhere, not even encrypted. It is impossible __even in principle__ for somebody to steal them out of this password manager, unless they have your master password (in which case you're obviously doomed) or they crack SHA256 or PBKDF2 (in which case we all are).
- Kinda like other password managers, you can easily get your passwords on a foreign computer. Just `pip install prpg && prpg compute example.com:username`. (Well... as with other password managers, typing your master password into a foreign computer is a terrible idea. But you may be interested in the `--mangle-master` command-line option, which, at the cost of some tedious manual work, lets you enter your master password in a way that ensures it can't be recovered unless the bad guys are straight-up snooping on this process's memory or the OS's RNG.)
- Unlike other password managers, you can carry this password manager around in your head. You just need to remember your master password and the algorithm. This lets you re-derive all of your passwords from scratch (if you're fairly computer-savvy), from memory, in under five minutes, using only extremely-widespread rigorously-specified algorithms that every major language has functionally-exactly-identical implementations of. You don't need to trust me. You are not reliant on me. If you lose access to this package, or stop trusting it, or something, you can re-implement the scheme on your own and recover all your passwords.

## Why is this bad?

- It doesn't store passwords, so you can't store your pre-existing passwords. (Yet. This might come.)
- If somebody steals your master password, they can rederive all your passwords. Other password managers kinda have this problem, but they at least require that the Bad Guy steal your vault-file too. (Unless the password manager is cloud-based, in which case you're super doomed.)
- The passwords this produces are hard to type and harder to remember. Copy-paste is the only way you'll find this useful.


## Installation/Usage

(First, install, with `pip install prpg`.)

Basic, standalone usage:

```bash
~ $ prpg compute 'example.com:username'
Master: ********
Copied password for 'example.com:username' to clipboard.
~ $
```

By default, this generates a 16-character password with all the major kinds of character (lower, upper, digit, punctuation) -- but this is customizable.

But with this usage, you have to remember all your sites/usernames/etc. -- and remember them _exactly_ -- and type them in each time. What a hassle!

For this reason, PRPG can maintain a list of strings (called "salts", for their cryptographic purpose) that it can easily fuzzy-search by prefix:

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

Each salt has a JSON object associated with it, which you can view using `prpg salts get SALTNAME`. You can store arbitrary information in this object (but remember it's stored in, effectively, plaintext! So nothing sensitive, please!):

```bash
~ $ addsalt 'blub.com:mylogin' --json '{"email address": "nobody@invalid.com", "birthday": "1970-01-01"}'
~ $ prpg salts get bl
{'birthday': '1970-01-01', 'email address': 'nobody@invalid.com'}
```

There are also three special keys that object can have:

- `postprocess` lets you write an arbitrary transformation on the password, using a Python lambda:

    ```bash
    ~ $ addsalt 'stupid-short-max-password-length.com:spencer' --json '{"postprocess": "lambda pw: pw[:12]"}'
    ~ $ prpg stu --print
    Chosen salt: 'stupid-short-max-password-length.com:spencer'
    Master: ********
    +viw/GniXPdg
    ~ $
    ```

    (Details: the string that gets passed to your lambda function is the full output of `base64(sha256(...))` -- that is to say, a 32-byte pseudorandom number, base64-encoded. This works out to 44 characters, all of which are completely pseudorandom and independent except the last two.)

- `salt` tells PRPG, "I know this salt is named `example.com:username`, but you should salt my master password with this other string instead." This might be useful if, say, a site changes its domain name.

    ```bash
    ~ $ prpg salts add 'blub-two-point-oh.com:mylogin' --json '{"salt": "blub.com:mylogin"}'
    ~ $ prpg recall blub.com --print
    Chosen salt: 'blub.com:mylogin'
    Master: ********
    EFX332fc3617Q1ZZAa0+
    ~ $ prpg recall blub-two --print
    Chosen salt: 'blub-two-point-oh.com:mylogin'
    Master: ********
    EFX332fc3617Q1ZZAa0+
    ```

- `xor` currently does nothing, but is reserved. (To enable storage of non-generated passwords, I'm considering adding this field that will be XORed with the generated password -- a sort of one-time pad. I'm not going to add this feature until I'm very sure there's a nice safe implementation, though.)

For more information about bells and whistles, consider running `prpg --help`.


## Internals/Reimplementation

In short:

- `base64(sha256(pbkdf2_hmac('sha256', master, salt, iterations=10**6)))`
- Default postprocessing: take the first 16 characters, and append `Aa0+` (the lowest-value base64 characters from each character-class used by base64, i.e. lower/upper/digit/punctuation, make a nice Schelling point).

I chose this to maximize "ease of re-implementing from memory, using only extremely-widespread, precisely-specified library functions," subject to the constraints "must be cryptographically respectable" and "must satisfy most password requirements by default."


### As Code

Here is the complete algorithm:

```python
import hashlib, base64

def master_and_salt_to_password(master: str, salt: str, postprocess=(lambda pw: pw[:16]+'Aa0+')) -> str:
  key = hashlib.pbkdf2_hmac(
          hash_name='sha256',
          password=master.encode('utf-8'),
          salt=salt.encode('utf-8'),
          iterations=10**6)
  sha = hashlib.sha256(key).digest()
  pw = base64.b64encode(sha).decode('utf-8')
  return postprocess(pw)
```
