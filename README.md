# philiprehberger-run-parallel

[![Tests](https://github.com/philiprehberger/py-run-parallel/actions/workflows/publish.yml/badge.svg)](https://github.com/philiprehberger/py-run-parallel/actions/workflows/publish.yml)
[![PyPI version](https://img.shields.io/pypi/v/philiprehberger-run-parallel.svg)](https://pypi.org/project/philiprehberger-run-parallel/)
[![License](https://img.shields.io/github/license/philiprehberger/py-run-parallel)](LICENSE)

Run multiple functions in parallel and collect results with the simplest possible API.

## Install

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

## API Reference

| Function / Class | Description |
|---|---|
| `parallel(*tasks, timeout=None) -> list` | Run callables or `(fn, *args)` tuples via `ThreadPoolExecutor`, return results in order. |
| `parallel_map(fn, items, *, workers=0, timeout=None) -> list` | Apply a function to each item in parallel, return results in order. |
| `aparallel(*coros) -> list` | Run async coroutines concurrently via `asyncio.gather`, return results in order. |
| `ParallelError` | Raised when any task fails. Has `.errors` (list of exceptions/None) and `.results` (list of values/None). |


## Development

```bash
pip install -e .
python -m pytest tests/ -v
```

## License

MIT
