import subprocess
import contextlib
import pexpect

def spawn_pow(subcommand):
  return pexpect.spawn('python -m pow '+subcommand)
