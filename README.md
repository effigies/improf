# improf

This import profiler is meant to be a lightweight diagnostic tool for identifying the costs of
a given import or series of imports.

Its operation is simple: You pass a series of modules to import, and between each import it takes
a snapshot of the current time, set of imported modules, and virtual memory allocation.

The difference between each snapshot is attributed to the import between each module, and the
set of new modules loaded in the final import is printed at the end.

There is very little to this package, and it doesn't try to be clever or identify the import
graph. It's a simple tool, and any cleverness is supplied by the user.

## Example

Suppose I want to find out what the major contributors are to `patsy`'s loading time and memory
footprint.

```Shell
> improf patsy
patsy: 441 modules; 299.79ms, 149.8MiB
Final: 441 modules; 299.79ms, 149.8MiB

Modules loaded with patsy:
{'_ast',
 '_bisect',
 '_blake2',
 [...]
 'bottleneck',
 'bottleneck.benchmark',
 [...]
 'calendar',
 'copy',
 'csv',
 'ctypes',
 'ctypes._endian',
 'cycler',
 'cython_runtime',
 'dateutil',
 'dateutil._common',
 [...]
 'decimal',
 'difflib',
 'dis',
 'distutils',
 'distutils.errors',
 'distutils.sysconfig',
 'distutils.version',
 'email',
 'email._encoded_words',
 [...]
 'gc',
 'gettext',
 'gzip',
 'hashlib',
 'http',
 'http.client',
 'inspect',
 'ipaddress',
 'json',
 'json.decoder',
 'json.encoder',
 'json.scanner',
 'locale',
 'logging',
 'matplotlib',
 'matplotlib._color_data',
 [...]
 'mmap',
 'mtrand',
 'ntpath',
 'numbers',
 'numpy',
 'numpy.__config__',
 [...]
 'opcode',
 'pandas',
 'pandas._libs',
 [...]
 'pathlib',
 'patsy',
 'patsy.build',
 [...]
 'pickle',
 'platform',
 'pprint',
 'pyparsing',
 'pytz',
 'pytz.exceptions',
 'pytz.lazy',
 'pytz.tzfile',
 'pytz.tzinfo',
 'quopri',
 'random',
 'six',
 'six.moves',
 'six.moves.urllib',
 'six.moves.urllib.request',
 'ssl',
 'string',
 'struct',
 'tempfile',
 'textwrap',
 'timeit',
 'unicodedata',
 'unittest',
 'unittest.case',
 [...]
 'urllib',
 'urllib.error',
 'urllib.parse',
 'urllib.request',
 'urllib.response',
 'uu'}
```

(Ellipses were added to reduce clutter.)

Looking through this, I may decide that `numpy` is likely the majority of the load time, so I would
insert it before `patsy`:

```Shell
> improf numpy patsy
numpy: 136 modules; 76.05ms, 116.4MiB
patsy: 305 modules; 218.12ms, 32.7MiB
Final: 441 modules; 294.17ms, 149.1MiB

Modules loaded with patsy:
{'_csv',
 '_cython_0_27_2',
 '_json',
 '_opcode',
 '_scproxy',
 '_ssl',
 'base64',
 'binascii',
 'bottleneck',
 'bottleneck.benchmark',
 [...]
 'calendar',
 'csv',
 'cycler',
 'dateutil',
 'dateutil._common',
 [...]
 'dis',
 'distutils',
 'distutils.errors',
 'distutils.sysconfig',
 'distutils.version',
 'email',
 'email._encoded_words',
 [...]
 'gzip',
 'http',
 'http.client',
 'inspect',
 'ipaddress',
 'json',
 'json.decoder',
 'json.encoder',
 'json.scanner',
 'matplotlib',
 'matplotlib._color_data',
 [...]
 'mmap',
 'opcode',
 'pandas',
 'pandas._libs',
 [...]
 'patsy',
 'patsy.build',
 [...]
 'platform',
 'pyparsing',
 'pytz',
 'pytz.exceptions',
 'pytz.lazy',
 'pytz.tzfile',
 'pytz.tzinfo',
 'quopri',
 'six',
 'six.moves',
 'six.moves.urllib',
 'six.moves.urllib.request',
 'ssl',
 'timeit',
 'unicodedata',
 'urllib.error',
 'urllib.request',
 'urllib.response',
 'uu'}
```

So numpy is about a quarter of the modules and import time, and possibly a good chunk of the VM
allocation (the first significant import you specify will often take the blame for a
disproportionate amount of VM...). Perhaps most of it is actually Pandas?

```Shell
> improf numpy pandas patsy
numpy: 136 modules; 74.99ms, 116.4MiB
pandas: 282 modules; 221.35ms, 32.9MiB
patsy: 23 modules; 12.90ms, 0.8MiB
Final: 441 modules; 309.24ms, 150.1MiB

Modules loaded with patsy:
{'patsy',
 'patsy.build',
 [...]
 'patsy.version'}
```

So we see `patsy` is pretty light, once you've imported Pandas.

## Tips

1. Re-run a couple times. The first run on a set of imports may be significantly slower than the
   second or third, but it usually stabilizes, in my experience.

2. When profiling your own projects, consider starting your list with your non-negotiable imports,
   followed by ones you're curious about the impact of, and finally your package.

3. Multiple modules may be imported in a single shot, which is usually helpful if you have a
   package with submodules that need to be specifically imported, but you're not interested in
   fingerprinting separately. For example, `scipy,scipy.stats,scipy.ndimage` might add a line
   like

       scipy: 275 modules; 263.28ms, 35.3MiB
    
   while `scipy scipy.stats scipy.ndimage` would add three lines:

       scipy: 10 modules; 2.57ms, 0.1MiB
       scipy.stats: 253 modules; 256.45ms, 34.7MiB
       scipy.ndimage: 12 modules; 47.27ms, 0.5MiB
