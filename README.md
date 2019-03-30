# aiodeduplicate [![CircleCI](https://circleci.com/gh/michalc/aiodeduplicate.svg?style=svg)](https://circleci.com/gh/michalc/aiodeduplicate) [![Test Coverage](https://api.codeclimate.com/v1/badges/5e70552f9dd435a18326/test_coverage)](https://codeclimate.com/github/michalc/aiodeduplicate/test_coverage)

Deduplicate concurrent asyncio Python coroutine calls. This offers a short-lived cache: for any given set of arguments, this cache lasts only for the length of a single call.


## Installation

```base
pip install aiodeduplicate
```

## Usage

For a coroutine whose arguments are hashable, you can create a _deduplicated_ version by passing it to `deduplicate_concurrent`. Any concurrent calls to this version that have the same arguments will result in only a _single_ run of original coroutine. 

For example, creating 3 concurrent invocations of a coroutine where 2 of them have identical arguments

```python
import asyncio
from aiodeduplicate import deduplicate_concurrent

async def main():
    deduplicated_coro = deduplicate_concurrent(coro)

    results = await asyncio.gather(*[
        deduplicated_coro('a'),
        deduplicated_coro('a'),
        deduplicated_coro('b'),
    ])
    print(results)

    await deduplicated_coro('a')

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

This would typically be used to deduplicate a function making calls to an API, and if

- you expect many concurrent calls;
- identical concurrent calls are idempotent;
- there are enough such calls that are identical to justify such a caching layer.

The function `deduplicate_concurrent` works with both coroutines, and functions that return a future.
