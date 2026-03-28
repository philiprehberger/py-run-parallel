# philiprehberger-run-parallel

[![Tests](https://github.com/philiprehberger/py-run-parallel/actions/workflows/publish.yml/badge.svg)](https://github.com/philiprehberger/py-run-parallel/actions/workflows/publish.yml)
[![PyPI version](https://img.shields.io/pypi/v/philiprehberger-run-parallel.svg)](https://pypi.org/project/philiprehberger-run-parallel/)
[![GitHub release](https://img.shields.io/github/v/release/philiprehberger/py-run-parallel)](https://github.com/philiprehberger/py-run-parallel/releases)
[![Last updated](https://img.shields.io/github/last-commit/philiprehberger/py-run-parallel)](https://github.com/philiprehberger/py-run-parallel/commits/main)
[![License](https://img.shields.io/github/license/philiprehberger/py-run-parallel)](LICENSE)
[![Bug Reports](https://img.shields.io/github/issues/philiprehberger/py-run-parallel/bug)](https://github.com/philiprehberger/py-run-parallel/issues?q=is%3Aissue+is%3Aopen+label%3Abug)
[![Feature Requests](https://img.shields.io/github/issues/philiprehberger/py-run-parallel/enhancement)](https://github.com/philiprehberger/py-run-parallel/issues?q=is%3Aissue+is%3Aopen+label%3Aenhancement)
[![Sponsor](https://img.shields.io/badge/sponsor-GitHub%20Sponsors-ec6cb9)](https://github.com/sponsors/philiprehberger)

Run multiple functions in parallel and collect results with the simplest possible API.

## Installation

```bash
pip install philiprehberger-run-parallel
```

## Usage

### Run functions in parallel

```python
from philiprehberger_run_parallel import parallel

results = parallel(
    lambda: 1 + 1,
    lambda: 2 + 2,
    lambda: 3 + 3,
)
# [2, 4, 6]
```

### Pass arguments with tuples

```python
from philiprehberger_run_parallel import parallel
import time

results = parallel(
    (time.sleep, 0.1),
    (pow, 2, 10),
)
# [None, 1024]
```

### Track progress

```python
from philiprehberger_run_parallel import parallel

def on_progress(completed, total):
    print(f"{completed}/{total} done")

results = parallel(
    lambda: 1 + 1,
    lambda: 2 + 2,
    lambda: 3 + 3,
    on_progress=on_progress,
)
# 1/3 done
# 2/3 done
# 3/3 done
```

### Process-based parallelism

```python
from philiprehberger_run_parallel import parallel_process

def cpu_work():
    return sum(range(10_000_000))

results = parallel_process([cpu_work, cpu_work, cpu_work], max_workers=3)
```

### Map a function over items

```python
from philiprehberger_run_parallel import parallel_map

results = parallel_map(str.upper, ["hello", "world"])
# ["HELLO", "WORLD"]

# Control the number of workers
results = parallel_map(fetch_url, urls, workers=8, timeout=30)
```

### Async parallel

```python
import asyncio
from philiprehberger_run_parallel import aparallel

async def main():
    results = await aparallel(
        fetch("https://example.com/a"),
        fetch("https://example.com/b"),
    )
    print(results)

asyncio.run(main())
```

### Error handling

```python
from philiprehberger_run_parallel import parallel, ParallelError

try:
    results = parallel(
        lambda: 1,
        lambda: 1 / 0,
    )
except ParallelError as e:
    print(e.errors)   # [None, ZeroDivisionError(...)]
    print(e.results)  # [1, None]
```

## API

| Function / Class | Description |
|---|---|
| `parallel(*tasks, timeout=None, on_progress=None) -> list` | Run callables or `(fn, *args)` tuples via `ThreadPoolExecutor`, return results in order. Optional progress callback `(completed, total)`. |
| `parallel_process(fns, max_workers=None) -> list` | Run callables via `ProcessPoolExecutor` for CPU-bound work, return results in order. |
| `parallel_map(fn, items, *, workers=0, timeout=None) -> list` | Apply a function to each item in parallel, return results in order. |
| `aparallel(*coros) -> list` | Run async coroutines concurrently via `asyncio.gather`, return results in order. |
| `ParallelError` | Raised when any task fails. Has `.errors` (list of exceptions/None) and `.results` (list of values/None). |

## Development

```bash
pip install -e .
python -m pytest tests/ -v
```

## Support

If you find this package useful, consider starring the repository.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Philip%20Rehberger-blue?logo=linkedin)](https://www.linkedin.com/in/philiprehberger/)
[![More Packages](https://img.shields.io/badge/More%20Packages-philiprehberger-orange)](https://github.com/philiprehberger?tab=repositories)

## License

[MIT](LICENSE)
