# shout out to Al and Automate the Boring Stuff

import sys

print('Enter the unit size (KB, MB, GB, or TB)')
unit = input('>')
if unit not in ['KB', 'kb', 'MB', 'mb', 'GB', 'gb', 'TB', 'tb']:
  print('Try something from the list...\nGoodbye')
  sys.exit()

if unit in ['kb', 'KB']:
  discrepancy = 1000 / 1024
if unit in ['mb', 'MB']:
  discrepancy = 1000000 / 1048576
if unit in ['gb', 'GB']:
  discrepancy = 1000000000 / 1073741824
if unit in ['tb', 'TB']:
  discrepancy = 1000000000000 / 1099511627776

print('Enter the advertised capacity:')
advertised = input('>')
advertised = float(advertised)

thetruth = str(round(advertised * discrepancy, 2))

print(f"Here's the truth. You only have {thetruth} {unit.upper()}s")