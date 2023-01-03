#!/usr/bin/env python
__version__ = '0.2.0'
import sys
import time


def fingerprint(mem=True):
    if mem:
        mem = P().memory_info().vms / (1024**2)
    return {'modules': set(sys.modules), 'time': time.time(), 'memory': mem}


FINGERPRINTS = [
    ('init', {'modules': set(), 'time': time.time(), 'memory': 0}),
    ('sys', fingerprint(False)),
]


def P():
    if P.ret is None:
        import psutil

        P.ret = psutil.Process()
    return P.ret


P.ret = None


def diff_fingerprint(y, x):
    return {
        'modules': y['modules'] - x['modules'],
        'time': y['time'] - x['time'],
        'memory': y['memory'] - x['memory'],
    }


def main():
    module_list = [arg.split(',') for arg in sys.argv[1:]]

    if ['--help'] in module_list:
        import os

        cmd = os.path.basename(sys.argv[0])
        print('Usage: {} MODULE_GROUP [MODULE_GROUP [...]]'.format(cmd))
        sys.exit(0)

    fingerprints = FINGERPRINTS.copy()
    show = []

    mem = module_list and module_list[0] != ['--no-mem']
    if mem and 'psutil' not in module_list[0]:
        module_list.insert(0, ['psutil'])
    else:
        module_list.pop(0)
    for modules in module_list:
        show_last = True
        if modules in (['--mem'], ['psutil']):
            mem = True
            modules = ['psutil']
        elif modules == ['--show']:
            show.append(fingerprints[-1][0])
            continue
        elif modules == ['--no-show']:
            show_last = False
            continue
        for module in modules:
            import_module(module)
        fingerprints.append((modules[0], fingerprint(mem)))

    if show_last:
        show.append(fingerprints[-1][0])

    diffs = {
        y[0]: diff_fingerprint(y[1], x[1])
        for y, x in zip(fingerprints[1:], fingerprints[:-1])
    }
    diffs['Final'] = diff_fingerprint(fingerprints[-1][1], fingerprints[0][1])

    for name, diff in diffs.items():
        print(
            f'{name}: {len(diff["modules"])} modules; '
            f'{diff["time"] * 1000:.02f}ms, {diff["memory"]:.01f}MiB'
        )

    from pprint import pprint

    for name in show:
        print(f'\nModules loaded with {name}:')
        pprint(diffs[name]['modules'])


from importlib import import_module

FINGERPRINTS.append(('importlib', fingerprint(False)))


if __name__ == '__main__':
    main()
