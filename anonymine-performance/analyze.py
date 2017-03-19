#!/usr/bin/pypy

import os
import sys


def main(filename, width, height, max_val):
    width -= 2
    data = list(map(float, open(filename).read().strip('\n').split('\n')))
    avg = sum(data)/len(data)
    
    data.sort()
    if len(data) % 2:
        median = data[len(data)//2]
    else:
        median = 0.5 * (data[len(data)//2 - 1] + data[len(data)//2])
    
    slice = max_val/width
    
    columns = [0] * width
    for i in range(width):
        for x in data:
            if i*slice < x <= (i+1)*slice:
                columns[i] += 1
    
    scale = float(height)/max(columns)
    
    bars = []
    for i in range(width):        
        char = ''
        if i*slice < min(data) <= (i+1)*slice:
            char += '['
        if i*slice < max(data) <= (i+1)*slice:
            char += ']'
        if i*slice < avg <= (i+1)*slice:
            char += 'A'
        if i*slice < median <= (i+1)*slice:
            char += 'M'

        y = int(scale*columns[i] + 0.5)
        
        if len(char) == 1 and not y:
            char = {'[': '(', ']': ')', 'M': 'm', 'A': 'a'}[char]
            y = 1
        elif len(char) > 1:
            char = '+'
        elif len(char) == 0:
            char = '|'
        
        bars.append(' '*(height-y) + char*y)
    
    for row in zip(*bars):
        sys.stdout.write(''.join(row) + '#\n')


if __name__ == '__main__':
    columns = int(os.getenv('COLUMNS', 80))
    lines = int(os.getenv('LINES', 24)) - 1
    
    cur_max = 0
    for filename in sys.argv[1:]:
        tmp = max(map(float, open(filename).read().strip('\n').split('\n')))
        if tmp > cur_max:
            cur_max = tmp
    
    lines //= len(sys.argv) - 1
    lines -= 1
    
    for filename in sys.argv[1:]:
        main(filename, columns, lines, cur_max)
        sys.stdout.write(filename + '\n')


