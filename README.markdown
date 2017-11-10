A one-line password manager.

Compared to other password managers:

- Pro: __secure,__ in that it doesn't store your passwords(!), and what isn't stored can't be stolen. Also, the core algorithm is simple enough that if you're a crypto nerd, you can personally verify that there's no room for anything to go wrong.
- Pro: __enables you to recover your passwords even if this software stops working__(!) as long as you have a handful of extremely-widespread cryptographic tools (like those in the Python's/Node's/Ruby's standard libraries).
- Con: __doesn't let you store your existing/custom passwords__ because all its passwords are auto-generated piles of hard-to-type mush (though, thanks to copy-paste, "hard-to-type" isn't usually an issue).
- Con: __no browser integration__ (yet). I know that's how normal people like their password managers.

## Table of Contents
- [Summary](#summary)
- [Advantages over other password managers](#advantages-over-other-password-managers)
- [Advantages of other password managers](#advantages-of-other-password-managers)
- [Installation/Usage](#installationusage)
- [Internals/Reimplemenation](#internalsreimplementation)

## Summary
The big idea: you have a master password. All your other passwords are, effectively, digital signatures: strings that are easy to produce for somebody who knows the master password, but prohibitively difficult to compute for somebody who doesn't.

It turns out that this is jaw-droppingly simple to implement:

![diagram](diagram.png)

In effect, this is a cryptographically secure pseudo-random password generator (hence the name, PRPG): a deterministic algorithm that maps seeds (i.e. [master, site] pairs) to passwords, in such a way that no number of [site, password] pairs will give you information about the passwords corresponding to any other sites.


## Advantages over other password managers

- Your passwords are not stored anywhere, not even encrypted. It is impossible __even in principle__ for somebody to steal them out of this password manager, unless they have your master password (in which case you're obviously doomed) or they crack SHA256 or PBKDF2 (in which case we all are).
- You can carry this password manager around in your head. By remembering only your master password and the algorithm, you can re-derive all of your passwords from scratch (if you're fairly computer-savvy), from memory, in under five minutes, using only extremely-widespread rigorously-specified algorithms that every major language has functionally-exactly-identical implementations of. You don't need to trust me. You are not reliant on me. If you lose access to this package, or stop trusting it, or something, you can re-implement the scheme on your own and recover all your passwords.
- At the expense of some tedious manual labor, you can enter your master password in a way that ensures it can't be recovered unless the bad guys are straight-up snooping on this process's memory or the OS's RNG.

## Advantages of other password managers

- Since this doesn't store passwords, you can't store your pre-existing passwords. (Yet. This might come.)
- If somebody steals your master password for this system, they can rederive all your passwords. Other password managers kinda have this problem, but they at least require that the Bad Guy steal your vault-file too. (Unless the password manager is cloud-based, in which case you're super doomed.)
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

There are also some special keys that objects can have, denoted by `__double-underscores__`:

- `__postprocess__` lets you write an arbitrary transformation on the password, using a Python lambda:

    ```bash
    ~ $ addsalt 'stupid-short-max-password-length.com:spencer' --json '{"__postprocess__": "lambda pw: pw[:12]"}'
    ~ $ prpg stu --print
    Chosen salt: 'stupid-short-max-password-length.com:spencer'
    Master: ********
    +viw/GniXPdg
    ~ $
    ```

    (Details: the string that gets passed to your lambda function is the full output of `base64(sha256(...))` -- that is to say, a 32-byte pseudorandom number, base64-encoded. This works out to 44 characters, all of which are completely pseudorandom and independent except the last two.)

- `__salt__` tells PRPG, "I know this salt is named `example.com:username`, but you should salt my master password with this other string instead." This might be useful if, say, a site changes its domain name.

    ```bash
    ~ $ prpg salts add 'blub-two-point-oh.com:mylogin' --json '{"__salt__": "blub.com:mylogin"}'
    ~ $ prpg recall blub.com --print
    Chosen salt: 'blub.com:mylogin'
    Master: ********
    EFX332fc3617Q1ZZAa0+
    ~ $ prpg recall blub-two --print
    Chosen salt: 'blub-two-point-oh.com:mylogin'
    Master: ********
    EFX332fc3617Q1ZZAa0+
    ```

(All other `__double-underscore__` keys are also reserved for future bells and whistles. All non-double-underscore keys are fair game.)

For more information about bells and whistles, consider running `prpg --help`.


## Internals/Reimplementation

In short:

- `base64(sha256(pbkdf2_hmac('sha256', master, salt, iterations=10**6)))`
- Default postprocessing: take the first 16 characters, and append `Aa0+` (the lowest-value base64 characters from each character-class used by base64, i.e. lower/upper/digit/punctuation, make a nice Schelling point).

I chose this to maximize "ease of re-implementing from memory, using only extremely-widespread, precisely-specified library functions," subject to the constraints "must be cryptographically respectable" and "must satisfy most password requirements by default."


### As Code

Here's the core algorithm in a variety of languages, for your copy-pasting pleasure:

* __Python:__

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
* __Node.js:__

    ```javascript
    crypto = require('crypto');
    function masterAndSaltToPassword(master, salt, postprocess=((s) => s.slice(0,16)+'Aa0+')) {
      key = crypto.pbkdf2Sync(master, salt, 10**6, 32, 'sha256');
      sha = crypto.createHash('sha256')
            .update(key)
            .digest();
      pw = sha.toString('base64');
      return postprocess(pw);
    }
    ```

* __JavaScript (for a web page):__

    ```javascript
    // base64js comes from https://raw.githubusercontent.com/beatgammit/base64-js/master/base64js.min.js
    function utf8encode(s) {return new TextEncoder('utf-8').encode(s);}
    function masterAndSaltToPassword(master, salt, postprocess=((s) => s.slice(0,16)+'Aa0+')) {
      return Subtle.importKey('raw', utf8encode(master), {name: 'PBKDF2', hash: 'SHA-256'}, false, ['deriveKey']).then((master) => {
        return Subtle.deriveKey({name: "PBKDF2", salt: utf8encode(salt), iterations: 10**6, hash: 'SHA-256'}, master, {name: 'HMAC', hash: 'SHA-256'}, true, ['sign']).then((key) => {
          return Subtle.exportKey('raw', key).then((exp) => {
            exp = exp.slice(0, 32);
            return Subtle.digest('SHA-256', exp).then((hash) => {
              var encoded = base64js.fromByteArray(new Uint8Array(hash));
              return encoded.slice(0, 16) + 'Aa0+';
            });
          });
        });
      });
    }
    ```

* __Ruby:__

    ```ruby
    require 'openssl'
    require 'base64'
    def master_and_salt_to_password(master, salt)
      key = OpenSSL::PKCS5.pbkdf2_hmac('foo', 'bar', 10**6, 32, OpenSSL::Digest::SHA256.new)
      sha = OpenSSL::Digest::SHA256.digest(key)
      result = Base64.encode64(sha)
      return (if block_given? then (yield result) else (result.slice(0, 16) + "Aa0+") end)
    end
    ```

* __Haskell:__

    ```haskell
    -- requires packages "cryptohash", "pbkdf", "base64-bytestring", "base16-bytestring"
    import Crypto.PBKDF (sha256PBKDF2)
    import qualified Crypto.Hash.SHA256 as SHA256
    import qualified Data.ByteString.UTF8 as UTF8
    import qualified Data.ByteString.Base64 as Base64
    import qualified Data.ByteString.Base16 as Base16

    defaultPostprocess :: String -> String
    defaultPostprocess s = (take 16 s) ++ "Aa0+"

    masterAndSaltToPassword :: String -> String -> String
    masterAndSaltToPassword master salt = (
      UTF8.toString $ Base64.encode $
      SHA256.hash $
      fst $ Base16.decode $ UTF8.fromString $ -- bytes <- hex string
      sha256PBKDF2 master salt (10^6) 32 -- hex string <- args
      )
    ```
