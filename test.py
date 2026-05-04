import sys

def calculate_average(numbers):
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)

def parse_input(args):
    numbers = []
    for arg in args:
        numbers.append(int(arg))
    return numbers

def main():
    if len(sys.argv) < 2:
        print("Usage: python app.py <numbers>")
        return

    numbers = parse_input(sys.argv[1:])
    avg = calculate_average(numbers)

    print(f"Average: {avg:.2f}")

if __name__ == "__main__":
    main()