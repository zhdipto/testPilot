# Input from user
num = int(input("Enter a number: "))

# Check Even or Odd
if num % 2 == 0:
    print(num, "is Even")
else:
    print(num, "is Odd")

# Check Prime or Not
if num <= 1:
    print(num, "is not a Prime number")
else:
    is_prime = True
    for i in range(2, int(num**0.5) + 1):
        if num % i == 0:
            is_prime = False
            break

    if is_prime:
        print(num, "is a Prime number")
    else:
        print(num, "is not a Prime number")