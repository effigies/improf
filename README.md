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
sys: 68 modules; 0.00ms, 0.0MiB
importlib: 0 modules; 0.00ms, 0.0MiB
psutil: 41 modules; 11.77ms, 19.4MiB
patsy: 493 modules; 198.46ms, 703.1MiB
Final: 602 modules; 210.23ms, 722.5MiB

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
sys: 68 modules; 0.00ms, 0.0MiB
importlib: 0 modules; 0.00ms, 0.0MiB
psutil: 41 modules; 11.80ms, 19.4MiB
numpy: 128 modules; 48.26ms, 660.1MiB
patsy: 365 modules; 122.67ms, 43.0MiB
Final: 602 modules; 182.74ms, 722.5MiB

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
sys: 68 modules; 0.00ms, 0.0MiB
importlib: 0 modules; 0.00ms, 0.0MiB
psutil: 41 modules; 11.91ms, 19.4MiB
numpy: 128 modules; 48.25ms, 660.1MiB
pandas: 342 modules; 119.37ms, 42.8MiB
patsy: 23 modules; 3.18ms, 0.1MiB
Final: 602 modules; 182.72ms, 722.4MiB

Modules loaded with patsy:
{'patsy',
 'patsy.build',
 [...]
 'patsy.version'}
```

So we see `patsy` is pretty light, once you've imported Pandas.

## Flag options

### `--(no-)mem`

Because we use psutil to collect memory footprints, you may miss imports in a tool
that are shared with psutil. If you pass `--no-mem` as the first flag, then psutil
is not loaded, and memory data is not collected until `--mem` or `psutil` is passed:

```console
> ./improf.py --no-mem numpy --mem pandas patsy
sys: 68 modules; 0.00ms, 0.0MiB
importlib: 0 modules; 0.00ms, 0.0MiB
numpy: 148 modules; 53.79ms, 0.0MiB
psutil: 21 modules; 10.63ms, 679.5MiB
pandas: 342 modules; 116.02ms, 42.8MiB
patsy: 23 modules; 3.19ms, 0.2MiB
Final: 602 modules; 183.63ms, 722.4MiB

Modules loaded with patsy:
{'patsy',
 'patsy.build',
 [...]
 'patsy.version'}
```

### `--(no-)show`

To avoid printing out the modules of the last import, add `--no-show` to the end of
the list. To print out the modules of a different import, add `--show` after that
import.

Combining with `--mem`/`--no-mem`, we can see the imports attributable to
subprocess, separate from psutil:

```console
> improf --no-mem subprocess --show --mem numpy --no-show
sys: 68 modules; 0.00ms, 0.0MiB
importlib: 0 modules; 0.00ms, 0.0MiB
subprocess: 10 modules; 2.15ms, 0.0MiB
psutil: 31 modules; 9.53ms, 19.4MiB
numpy: 128 modules; 47.15ms, 660.1MiB
Final: 237 modules; 58.84ms, 679.5MiB

Modules loaded with subprocess:
{'_posixsubprocess',
 '_weakrefset',
 'collections.abc',
 'fcntl',
 'math',
 'select',
 'selectors',
 'signal',
 'subprocess',
 'threading'}
```

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
