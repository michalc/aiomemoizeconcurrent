import asyncio
from unittest import (
    TestCase,
)
from unittest.mock import (
    Mock,
    call,
)

from aiodeduplicate import (
    deduplicate_concurrent,
)


def async_test(func):
    def wrapper(*args, **kwargs):
        future = func(*args, **kwargs)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(future)
    return wrapper


def until_called(num_times):
    num_times_called = 0
    future = asyncio.Future()

    def func():
        nonlocal num_times_called
        num_times_called += 1
        if num_times_called == num_times:
            future.set_result(None)
        return future

    return func


class TestDeduplicate(TestCase):

    @async_test
    async def test_identical_concurrent_deduplicated_coroutine(self):
        loop = asyncio.get_event_loop()
        mock = Mock()

        async def func(*args, **kwargs):
            mock(*args, **kwargs)
            # Yield so the other task can run
            await asyncio.sleep(0)
            return 'value'

        deduplicated = deduplicate_concurrent(func)

        task_a = asyncio.ensure_future(deduplicated(10, 20, a='val_a', b='val_b'))
        task_b = asyncio.ensure_future(deduplicated(10, 20, a='val_a', b='val_b'))

        task_a_result = await task_a
        task_b_result = await task_b
        self.assertEqual(task_a_result, 'value')
        self.assertEqual(task_b_result, 'value')
        self.assertEqual(mock.mock_calls, [call(10, 20, a='val_a', b='val_b')])

    @async_test
    async def test_identical_concurrent_deduplicated_future(self):
        loop = asyncio.get_event_loop()
        mock = Mock()
        future = asyncio.Future()

        def func(*args, **kwargs):
            mock(*args, **kwargs)
            return future

        deduplicated = deduplicate_concurrent(func)

        task_a = asyncio.ensure_future(deduplicated(10, 20, a='val_a', b='val_b'))
        task_b = asyncio.ensure_future(deduplicated(10, 20, a='val_a', b='val_b'))

        await asyncio.sleep(0)
        future.set_result('value')

        task_a_result = await task_a
        task_b_result = await task_b
        self.assertEqual(task_a_result, 'value')
        self.assertEqual(task_b_result, 'value')
        self.assertEqual(mock.mock_calls, [call(10, 20, a='val_a', b='val_b')])

    @async_test
    async def test_different_concurrent_not_deduplicated(self):
        loop = asyncio.get_event_loop()
        mock = Mock()
        func_done = asyncio.Event()
        until_called_twice = until_called(num_times=2)

        async def func(*args, **kwargs):
            mock(*args, **kwargs)
            await until_called_twice()
            return 'value'

        deduplicated = deduplicate_concurrent(func)

        task_a = asyncio.ensure_future(deduplicated(10, 20, a='val_a', b='val_b'))
        task_b = asyncio.ensure_future(deduplicated(10, 20, a='val_a', b='val_d'))

        task_a_result = await task_a
        task_b_result = await task_b
        self.assertEqual(task_a_result, 'value')
        self.assertEqual(task_b_result, 'value')
        self.assertEqual(mock.mock_calls, [
            call(10, 20, a='val_a', b='val_b'),
            call(10, 20, a='val_a', b='val_d'),
        ])

    @async_test
    async def test_identical_sequential_not_deduplicated(self):
        loop = asyncio.get_event_loop()
        mock = Mock()

        async def func(*args, **kwargs):
            mock(*args, **kwargs)
            return 'value'

        deduplicated = deduplicate_concurrent(func)

        task_a = asyncio.ensure_future(deduplicated(10, 20, a='val_a', b='val_b'))
        task_a_result = await task_a

        task_b = asyncio.ensure_future(deduplicated(10, 20, a='val_a', b='val_b'))

        task_b_result = await task_b
        self.assertEqual(task_a_result, 'value')
        self.assertEqual(task_b_result, 'value')
        self.assertEqual(mock.mock_calls, [
            call(10, 20, a='val_a', b='val_b'),
            call(10, 20, a='val_a', b='val_b'),
        ])

    @async_test
    async def test_identical_concurrent_deduplicated_exception(self):
        loop = asyncio.get_event_loop()
        mock = Mock()

        async def func(*args, **kwargs):
            mock(*args, **kwargs)
            # Yield so the other task can run
            await asyncio.sleep(0)
            raise Exception('inner')

        deduplicated = deduplicate_concurrent(func)

        task_a = asyncio.ensure_future(deduplicated(10, 20, a='val_a', b='val_b'))
        task_b = asyncio.ensure_future(deduplicated(10, 20, a='val_a', b='val_b'))

        with self.assertRaisesRegex(Exception, 'inner'):
            await task_a

        with self.assertRaisesRegex(Exception, 'inner'):
            await task_b

        self.assertEqual(mock.mock_calls, [call(10, 20, a='val_a', b='val_b')])

    @async_test
    async def test_identical_concurrent_deduplicated_cancelled(self):
        loop = asyncio.get_event_loop()
        mock = Mock()
        called = asyncio.Event()

        async def func(*args, **kwargs):
            mock(*args, **kwargs)
            called.set()
            await asyncio.Future()

        deduplicated = deduplicate_concurrent(func)

        task_a = asyncio.ensure_future(deduplicated(10, 20, a='val_a', b='val_b'))
        task_b = asyncio.ensure_future(deduplicated(10, 20, a='val_a', b='val_b'))
        await called.wait()
        task_a.cancel()

        with self.assertRaises(asyncio.CancelledError):
            await task_b
