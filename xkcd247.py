#!/usr/bin/python

import sys
import time


def factor(number):
    # number is <= 2359 so use the most naive solution possible.
    if not number:
        return [0]
    p = 2
    factors = []
    while number != 1:
        if number % p:
            p += 1
        else:
            number //= p
            factors.append(p)
    return factors

def round():
    now = time.strftime('%H:%M')
    correct = factor(int(time.strftime('%H%M'), 10))
    
    sys.stdout.write('Think fast. {}! '.format(now))
    sys.stdout.flush()
    
    entered = sys.stdin.readline().strip()
    if now != time.strftime('%H:%M'):
        sys.stdout.write('Too late\n')
        return False
    
    try:
        entered = sorted(filter(
            lambda x: x != 1,
            map(
                lambda y: int(y.strip()),
                entered.replace('x', '*').split('*')
            )
        ))
    except ValueError:
        sys.stdout.write('Guess what? WRONG!\n')
        return False
    
    if entered == correct:
        return True
    else:
        sys.stdout.write('Wrong!\n')
        return False


def game(lives=1):
    score = 0    
    spinner = "|/-\\"
    spinner_index = 0
    while lives:
        try:
            # Wait till the beginning of a minute.
            while int(time.time()) % 60:
                sys.stdout.write('\b' + spinner[spinner_index])
                sys.stdout.flush()
                spinner_index = (spinner_index + 1) % 4
                time.sleep(.7)
            sys.stdout.write('\b')
            
            if round():
                score += 60 - int(time.time())%60
            else:
                lives -= 1
            sys.stdout.write('Score: {}\tLives: {}\n'.format(score, lives))
        except KeyboardInterrupt:
            return score


def main():
    sys.stdout.write('How long can you factor the time?\n')
    sys.stdout.write('Example: Think fast. 19:42! 2*971\n')
    sys.stdout.write('Example: Think fast. 19:43! 29x67\n')
    sys.stdout.write('\n')
    
    game(2)


if __name__ == '__main__':
    main()


