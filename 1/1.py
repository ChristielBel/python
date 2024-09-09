n = int(input())

hours = (n // 60) % 24
minutes = n % 60

print(f"{hours} hours, {minutes} minutes")
