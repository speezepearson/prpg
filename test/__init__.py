import subprocess
import re
import pexpect

def spawn_prpg(subcommand):
  return pexpect.spawn('python -m prpg '+subcommand)

def expect_exact_line(p, string, timeout=3):
  p.expect(r'\n' + re.escape(string) + r'\r?\n')
