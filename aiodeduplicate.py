import asyncio
import collections


def deduplicate_concurrent(func):

    concurrent = {}

    async def deduplicated(*args, **kwargs):
        identifier = (args, tuple(kwargs.items()))

        if identifier in concurrent:
            return await concurrent[identifier]
        
        future = asyncio.Future()
        concurrent[identifier] = future

        try:
            result = await func(*args, **kwargs)
        except BaseException as exception:
            future.set_exception(exception)
        else:
            future.set_result(result)
        finally:
            del concurrent[identifier]

        return await future

    return deduplicated
