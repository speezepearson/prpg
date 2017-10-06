import sys
import subprocess

class UnknownPlatformError(Exception):
  pass

def copy_to_clipboard(s):
  if sys.platform.startswith('linux'):
    subprocess.Popen(['xsel', '--input', '--clipboard'], stdin=subprocess.PIPE).communicate(s.encode())
  elif sys.platform.startswith('darwin'):
    subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE).communicate(s.encode())
  elif sys.platform.startswith('win32'):
    subprocess.Popen(['clip'], stdin=subprocess.PIPE).communicate(s.encode())
  elif sys.platform.startswith('cygwin'):
    open('/dev/clipboard', 'w').write(s.encode())
  else:
    raise UnknownPlatformError(sys.platform)
