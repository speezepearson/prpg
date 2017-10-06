import subprocess
import sys

def get_seed():
  result = subprocess.Popen(['/bin/bash', '-c', 'read -s -p "Seed: " SEED && export SEED && env | sed -n -e "s/^SEED=//p"'], stdout=subprocess.PIPE).communicate()[0].decode().strip()
  if sys.stdout.isatty():
    print()
  return result
