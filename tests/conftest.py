import asyncio

import pytest


@pytest.yield_fixture
def event_loop(event_loop):
    """Create an instance of the default event loop for each test case."""
    # policy = asyncio.get_event_loop_policy()
    # res = policy.new_event_loop()
    # asyncio.set_event_loop(res)
    event_loop._close = event_loop.close
    event_loop.close = lambda: None

    yield event_loop

    event_loop._close()
