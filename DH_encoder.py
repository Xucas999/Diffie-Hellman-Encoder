import math
import random

def get_prime(generator_number_min, generator_number_max):
    print("Finding Prime Numbers...")
    # This function uses Fermat's Factorisation to identify two prime numbers a+b and a-b
    # It returns the larger of these two prime numbers

    # p = a + b
    # q = a - b
    generator_number = random.randint(generator_number_min, generator_number_max)
    while generator_number%2 == 0:
        generator_number = random.randint(generator_number_min, generator_number_max)

    a = int(math.sqrt(generator_number)) 
    if a**2 == generator_number:
        a -= 1
    a += 1
    while True:
        bb = a**2 - generator_number
        b = math.sqrt(bb)
        if b.is_integer():
            break
        print(generator_number, a, b)
        a += 1
    return int(a + b)

def calculate_public_shared_values(secret_number, base_number, big_prime):
    return (base_number ** secret_number) % big_prime

def calculate_shared_secret(public_value, secret_number, big_prime):
    return (public_value ** secret_number) % big_prime
