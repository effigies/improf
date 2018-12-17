#!/usr/bin/env python
import sys
import psutil
import time
from importlib import import_module

__version__ = '0.1.1'

P = psutil.Process()


def fingerprint():
    return {'modules': set(sys.modules),
            'time': time.time(),
            'memory': P.memory_info().vms / (1024 ** 2)}


def diff_fingerprint(y, x):
    return {'modules': y['modules'] - x['modules'],
            'time': y['time'] - x['time'],
            'memory': y['memory'] - x['memory']}


def main():
    module_list = [['sys']] + [arg.split(',') for arg in sys.argv[1:]]

    if module_list == [['sys']]:
        import os
        cmd = os.path.basename(sys.argv[0])
        print("Usage: {} MODULE_GROUP [MODULE_GROUP [...]]".format(cmd))
        sys.exit(0)

    fingerprints = []

    for modules in module_list:
        for module in modules:
            import_module(module)
        fingerprints.append((modules[0], fingerprint()))

    diffs = [
        (y[0], diff_fingerprint(y[1], x[1]))
        for y, x in zip(fingerprints[1:], fingerprints[:-1])]
    diffs.append(('Final', diff_fingerprint(fingerprints[-1][1], fingerprints[0][1])))

    for name, diff in diffs:
        print("{}: {} modules; {:.02f}ms, {:.01f}MiB".format(name, len(diff['modules']),
                                                             diff['time'] * 1000,
                                                             diff['memory']))

    print('\nModules loaded with {}:'.format(diffs[-2][0]))
    from pprint import pprint
    pprint(diffs[-2][1]['modules'])


if __name__ == '__main__':
    main()
