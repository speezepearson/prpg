import subprocess
import contextlib
import pexpect

def spawn_prpg(subcommand):
  return pexpect.spawn('python -m prpg '+subcommand)
