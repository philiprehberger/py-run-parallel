from __future__ import annotations

import asyncio
import os
import threading
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from typing import Any, Callable, Iterable, TypeVar

__all__ = ["parallel", "parallel_map", "parallel_process", "aparallel", "ParallelError"]

T = TypeVar("T")


class ParallelError(Exception):
    """Raised when one or more parallel tasks fail.

    Attributes:
        errors: List of exceptions from failed tasks, ``None`` for tasks that
            succeeded.
        results: List of results from all tasks.  Failed task slots contain
            ``None``.
    """

    def __init__(
        self,
        message: str,
        *,
        errors: list[BaseException | None],
        results: list[Any],
    ) -> None:
        super().__init__(message)
        self.errors = errors
        self.results = results


def parallel(
    *tasks: Callable[[], Any] | tuple[Callable[..., Any], ...],
    timeout: float | None = None,
    on_progress: Callable[[int, int], None] | None = None,
) -> list[Any]:
    """Run callables in parallel and return results in submission order.

    Each *task* is either a no-argument callable or a tuple of
    ``(callable, *args)`` / ``(callable, *args, **kwargs)``.

    Args:
        *tasks: Callables or ``(fn, *args)`` tuples to execute.
        timeout: Maximum seconds to wait for all tasks.  ``None`` means no
            limit.
        on_progress: Optional callback invoked after each task completes.
            Receives ``(completed_count, total_count)``.

    Returns:
        A list of return values, one per task, in the same order they were
        passed in.

    Raises:
        ParallelError: If any task raises an exception.  The error carries
            both ``.errors`` and ``.results`` so callers can inspect partial
            outcomes.
    """
    if not tasks:
        return []

    n = len(tasks)
    results: list[Any] = [None] * n
    errors: list[BaseException | None] = [None] * n
    completed = 0
    lock = threading.Lock()

    with ThreadPoolExecutor() as executor:
        future_to_idx = {}
        for idx, task in enumerate(tasks):
            if isinstance(task, tuple):
                fn, *args = task
                future = executor.submit(fn, *args)
            else:
                future = executor.submit(task)
            future_to_idx[future] = idx

        for future in as_completed(future_to_idx, timeout=timeout):
            idx = future_to_idx[future]
            try:
                results[idx] = future.result()
            except Exception as exc:
                errors[idx] = exc

            if on_progress is not None:
                with lock:
                    completed += 1
                    on_progress(completed, n)

    if any(e is not None for e in errors):
        failed = sum(1 for e in errors if e is not None)
        raise ParallelError(
            f"{failed} of {n} tasks failed",
            errors=errors,
            results=results,
        )

    return results


def parallel_process(
    fns: list[Callable[..., Any]],
    max_workers: int | None = None,
) -> list[Any]:
    """Run callables in parallel using processes and return results in order.

    Uses ``ProcessPoolExecutor`` instead of ``ThreadPoolExecutor``, making
    it suitable for CPU-bound work that benefits from true parallelism.

    Args:
        fns: List of no-argument callables to execute.
        max_workers: Maximum number of processes.  ``None`` lets the runtime
            choose (typically ``os.cpu_count()``).

    Returns:
        A list of return values, one per callable, in the same order.

    Raises:
        ParallelError: If any callable raises an exception.
    """
    if not fns:
        return []

    n = len(fns)
    results: list[Any] = [None] * n
    errors: list[BaseException | None] = [None] * n

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        future_to_idx = {
            executor.submit(fn): idx for idx, fn in enumerate(fns)
        }

        for future in as_completed(future_to_idx):
            idx = future_to_idx[future]
            try:
                results[idx] = future.result()
            except Exception as exc:
                errors[idx] = exc

    if any(e is not None for e in errors):
        failed = sum(1 for e in errors if e is not None)
        raise ParallelError(
            f"{failed} of {n} tasks failed",
            errors=errors,
            results=results,
        )

    return results


def parallel_map(
    fn: Callable[..., T],
    items: Iterable[Any],
    *,
    workers: int = 0,
    timeout: float | None = None,
) -> list[T]:
    """Apply *fn* to each item in parallel and return results in order.

    Args:
        fn: A callable that accepts a single positional argument.
        items: Iterable of arguments to map over.
        workers: Maximum number of threads.  ``0`` (the default) lets the
            runtime choose (typically ``min(32, os.cpu_count() + 4)``).
        timeout: Maximum seconds to wait for all tasks.

    Returns:
        A list of results in the same order as *items*.

    Raises:
        ParallelError: If any invocation raises an exception.
    """
    items_list = list(items)
    if not items_list:
        return []

    n = len(items_list)
    max_workers = workers if workers > 0 else min(32, (os.cpu_count() or 1) + 4)
    results: list[Any] = [None] * n
    errors: list[BaseException | None] = [None] * n

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_idx = {
            executor.submit(fn, item): idx for idx, item in enumerate(items_list)
        }

        for future in as_completed(future_to_idx, timeout=timeout):
            idx = future_to_idx[future]
            try:
                results[idx] = future.result()
            except Exception as exc:
                errors[idx] = exc

    if any(e is not None for e in errors):
        failed = sum(1 for e in errors if e is not None)
        raise ParallelError(
            f"{failed} of {n} tasks failed",
            errors=errors,
            results=results,
        )

    return results


async def aparallel(*coros: Any) -> list[Any]:
    """Run coroutines concurrently and return results in order.

    This is a thin wrapper around :func:`asyncio.gather` that raises
    :class:`ParallelError` on failure instead of propagating the first
    exception.

    Args:
        *coros: Awaitable coroutines to execute concurrently.

    Returns:
        A list of results in the same order as the coroutines.

    Raises:
        ParallelError: If any coroutine raises an exception.
    """
    if not coros:
        return []

    n = len(coros)
    completed = await asyncio.gather(*coros, return_exceptions=True)

    results: list[Any] = [None] * n
    errors: list[BaseException | None] = [None] * n

    for idx, value in enumerate(completed):
        if isinstance(value, BaseException):
            errors[idx] = value
        else:
            results[idx] = value

    if any(e is not None for e in errors):
        failed = sum(1 for e in errors if e is not None)
        raise ParallelError(
            f"{failed} of {n} tasks failed",
            errors=errors,
            results=results,
        )

    return results
