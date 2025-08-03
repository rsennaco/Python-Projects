import random

def shake_the_ball(response):
  if response == 1:
    return 'It is certain'
  elif response == 2:
    return 'It is decidedly so'
  elif response == 3:
    return 'Yes'
  elif response == 4:
    return 'Reply hazy try again'
  elif response == 5:
    return 'Ask again later'
  elif response == 6:
    return 'Concentrate and ask again'
  elif response == 7:
    return 'My reply is no'
  elif response == 8:
    return 'Outlook not so good'
  elif response == 9:
    return 'Very doubtful'

while True:
  print('Ask a yes or no question:')
  input('>')
  print(shake_the_ball(random.randint(1, 9)))
  print('\nWant to ask again?')
  again = input('(y/n)\n>')
  if again in ['n', 'N', 'no', 'No']:
    break