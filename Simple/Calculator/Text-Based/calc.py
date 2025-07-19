# calc is short for calculator btw

def add(x, y):
  return x + y

def subtract(x, y):
  return x - y

def multiply(x, y):
  return x * y

def divide(x, y):
  return x / y

while True:
  choice = int(input("""
Select an operation.
1. Add
2. Subtract
3. Multiply
4. Divide
Selection:"""))
  
  if choice not in (1, 2, 3, 4):
    print("Maybe select from the list and not...whatever that was.")
    continue

  try:
    num1 = float(input("Enter first number: "))
    num2 = float(input("Enter second number: "))
  except ValueError:
    print("That's not a number big dog...")
    continue

  if choice == 1:
    print(f"{num1} + {num2} = {add(num1, num2)}")

  elif choice == 2:
    print(num1, "-", num2, "=", subtract(num1, num2))

  elif choice == 3:
    print(num1, "x", num2, "=", multiply(num1, num2))

  elif choice == 4:
    try:
      result = divide(num1, num2)
    except ZeroDivisionError:
      print("Cant divide by zero")
    else:
      print(num1, "/", num2, "=", divide(num1, num2))

  again = input("Again? (y/n)\n")
  if again.lower() == "n":
    print("Later")
    break