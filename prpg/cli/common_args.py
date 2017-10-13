import os

def add_salt_file_argument(parser):
  parser.add_argument(
    '-f', '--salt-file',
    default=os.path.join(os.environ['HOME'], '.prpg-salts.json'),
    help='ROT13ed JSON file containing information about various applications (default ~/.prpg-salts.json)')

def add_mangle_master_argument(parser):
  parser.add_argument('--mangle-master', action='store_true', help='enter master password in a laborious, char-by-char-mangled way if you are worried about keyloggers')

def add_print_argument(parser):
  parser.add_argument(
    '--print', action='store_true',
    help='print output instead of copying to clipboard')

def add_query_argument(parser):
  parser.add_argument('query', help='regular expression matching beginning of desired salt')

def add_confirm_argument(parser):
  parser.add_argument(
    '--confirm', action='store_true',
    help='ask for master password twice to ensure you type it right')
