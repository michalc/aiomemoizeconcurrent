# aiomemoizeconcurrent [![CircleCI](https://circleci.com/gh/michalc/aiomemoizeconcurrent.svg?style=svg)](https://circleci.com/gh/michalc/aiomemoizeconcurrent) [![Test Coverage](https://api.codeclimate.com/v1/badges/5e70552f9dd435a18326/test_coverage)](https://codeclimate.com/github/michalc/aiomemoizeconcurrent/test_coverage)

Memoize concurrent asyncio Python coroutine calls. This offers short-lived memoization: for any given set of arguments, the cache lasts only for the length of a single call.


## Installation

```base
pip install aiomemoizeconcurrent
```

## Usage

For a coroutine whose arguments are hashable, you can create a _memoized_ version by passing it to `memoize_concurrent`. Any concurrent calls to this version that have the same arguments will result in only a _single_ run of original coroutine. 

For example, creating 3 concurrent invocations of a coroutine where 2 of them have identical arguments

```python
import asyncio
from aiomemoizeconcurrent import memoize_concurrent

async def main():
    memoized_coro = memoize_concurrent(coro)

    results = await asyncio.gather(*[
        memoized_coro('a'),
        memoized_coro('a'),
        memoized_coro('b'),
    ])
    print(results)

    await memoized_coro('a')

async def coro(value):
    print('Inside coro', value)
    await asyncio.sleep(1)
    return value

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()
```

will only run `coro` twice, as shown by the output

```
Inside coro a
Inside coro b
['a', 'a', 'b']
```


## Use cases

This can be used to memoize a function making calls to an API, and especially if

- you expect many concurrent calls;
- identical concurrent calls are idempotent;
- there are enough such calls that are identical to justify such a caching layer.

It can also be used to avoid concurrency edge cases/race conditions with multiple tasks accessing shared resources. For example, multiple tasks may need to dynamically create shared UDP sockets. To ensure that this dynamic generation isn't called by multiple tasks at the same time for the same address, it can be wrapped with `memoize_concurrent`.

The function `memoize_concurrent` works with both coroutines, and functions that return a future.
