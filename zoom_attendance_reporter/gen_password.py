"""
Generate a random password comprised of 4 of these words.
"""
from random import randint

def gen_password():
    with open('secret_words.txt', 'r') as wordsf:
        words = wordsf.read().split(',')
    return '-'.join([words[randint(0, len(words) - 1)].lower() for _ in range(4)])

if __name__ == '__main__':
    print(gen_password())
