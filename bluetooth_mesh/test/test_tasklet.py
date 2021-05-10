from asyncio import Task
from asyncio.events import AbstractEventLoop
from asyncio.futures import Future
from asyncio.locks import Event
from asyncio.tasks import gather, wait_for
from functools import partial

import pytest

from bluetooth_mesh.utils import tasklet


@pytest.mark.asyncio
async def test_tasklet_executes_callback(event_loop: AbstractEventLoop):
    status = event_loop.create_future()

    @tasklet
    async def set_code(code):
        status.set_result(code)

    await set_code("ok!")

    result = await wait_for(status, timeout=1)
    assert result == "ok!"


@pytest.mark.asyncio
async def test_tasklet_one_after_another(event_loop: AbstractEventLoop):
    statuses = [event_loop.create_future(), event_loop.create_future()]

    @tasklet
    async def set_ok(status):
        status.set_result("ok!")

    await set_ok(statuses[0])
    await wait_for(statuses[0], timeout=1)
    await set_ok(statuses[1])
    await wait_for(statuses[1], timeout=1)

    assert statuses[0].result() == statuses[1].result() == "ok!"


@pytest.mark.asyncio
async def test_tasklet_cancellation(event_loop: AbstractEventLoop):
    gates = [Event(), Event()]
    statuses = [event_loop.create_future(), event_loop.create_future()]

    def on_done(status: Future, task: Future) -> None:
        status.set_result("cancelled" if task.cancelled() else "done")

    @tasklet
    async def suspend(e: Event):
        await e.wait()

    (await suspend(gates[0])).add_done_callback(partial(on_done, statuses[0]))
    # Next call should cancel the previously scheduled task
    (await suspend(gates[1])).add_done_callback(partial(on_done, statuses[1]))
    # Opening the gate should complete the newly scheduled task
    gates[1].set()

    await wait_for(gather(*statuses), timeout=1)

    assert statuses[0].result() == "cancelled"
    assert statuses[1].result() == "done"


@pytest.mark.asyncio
async def test_tasklet_grouping(event_loop: AbstractEventLoop):
    no_tasks = 2
    gates = [Event() for _ in range(no_tasks)]
    statuses = [event_loop.create_future() for _ in range(no_tasks)]

    def on_done(status: Future, task: Task) -> None:
        status.set_result("cancelled" if task.cancelled() else "done")

    def group_by(_, group: int) -> int:
        return group

    @tasklet
    async def suspend(e: Event, group: int):
        await e.wait()

    suspend.group_by = group_by

    (await suspend(gates[0], group=1)).add_done_callback(partial(on_done, statuses[0]))
    (await suspend(gates[1], group=2)).add_done_callback(partial(on_done, statuses[1]))

    for g in gates:
        g.set()

    await wait_for(gather(*statuses), timeout=1)

    assert statuses[0].result() == "done"
    assert statuses[1].result() == "done"
