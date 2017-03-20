#!/usr/bin/pypy

import random
import sys
import time

import anonymine_fields
import anonymine_solver


def profile_solver(x, y, m):
    field = anonymine_fields.generic_field([x, y])
    mines = field.all_cells()
    random.shuffle(mines)
    field.fill(mines[:m])
    for mine in mines[m:]:
        for neighbour in field.get_neighbours(mine):
            if neighbour in mines[:m]:
                break
        else:
            field.reveal(mine)
            break
    solver = anonymine_solver.solver()
    solver.field = field
    start = time.time()
    result = solver.solve()
    return result[0], result[1]['T']


def stats(data):
    # *** Stats from unorder data
    n = len(data)
    avg = sum(data)/n
    sdev = sum([(x - avg)**2 for x in data])/n
    low = min(data)
    high = max(data)
    # *** Stats from ordered data
    data.sort()
    # median
    if n%2:
        median = data[n//2]
    else:
        median = .5 * (data[n//2 - 1] + data[n//2])
    # avg-median displacement
    try:
        index = 0
        while data[index] < avg:
            index += 1
    except IndexError:
        index = n + 1
    index -= n//2
    index /= float(n)
    # Print data
    sys.stderr.write(
        '#{}\t'
        'Range: {:8f}-{:8f},   '
        'Average: {:8f}, Standard deviation: {:8f},   '
        'Median: {:8f}, Average line: median {:+d}%\n'.format(
            n,
            low, high,
            avg, sdev,
            median, int(index*100)
        )
    )

def main(x, y, m):
    filenames = {
        'all': 'attempt-time-{}@{}x{}'.format(m, x, y),
        True: 'attempt-time-{}@{}x{}-success'.format(m, x, y),
        False: 'attempt-time-{}@{}x{}-failure'.format(m, x, y),
    }
    try:
        filename = filenames['all']
        data = list(map(float, open(filename).read().strip('\n').split('\n')))
    except IOError:
        data = []
    
    logs = {key: open(filenames[key], 'a') for key in filenames}
    try:
        while True:
            success, new_time = profile_solver(x, y, m)
            for log in (logs['all'], logs[success]):
                log.write('{}\n'.format(new_time))
                log.flush()
                
            data.append(new_time)
            data.sort()
            stats(data)
    except KeyboardInterrupt:
        pass
    for key in logs:
        logs[key].close()


if __name__ == '__main__':
    if len(sys.argv) == 4:
        main(*map(int, sys.argv[1:]))
    else:
        main(20, 20, 80)
    

