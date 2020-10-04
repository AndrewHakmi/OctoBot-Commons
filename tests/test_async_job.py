#  Drakkar-Software OctoBot-Commons
#  Copyright (c) Drakkar-Software, All rights reserved.
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3.0 of the License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library.
import asyncio
import os
import time

from mock import AsyncMock, patch
import pytest

from octobot_commons.async_job import AsyncJob
from octobot_commons.asyncio_tools import wait_asyncio_next_cycle

pytestmark = pytest.mark.asyncio


async def callback():
    pass


async def test_has_enough_time_elapsed():
    job = AsyncJob(callback)
    if not os.getenv('CYTHON_IGNORE'):
        assert job._has_enough_time_elapsed()
        job.last_execution_time = time.time()
        assert job._has_enough_time_elapsed()
    job.stop()


async def test_has_enough_time_elapsed_with_delays():
    job = AsyncJob(callback, min_execution_delay=0.2)
    if not os.getenv('CYTHON_IGNORE'):
        assert job._has_enough_time_elapsed()
        job.last_execution_time = time.time()
        assert not job._has_enough_time_elapsed()
        await asyncio.sleep(0.2)
        assert job._has_enough_time_elapsed()
    job.stop()


async def test_should_run_with_dependencies():
    job2 = AsyncJob(callback)
    job3 = AsyncJob(callback)
    job = AsyncJob(callback)
    job.add_job_dependency(job2)
    job.add_job_dependency(job3)
    if not os.getenv('CYTHON_IGNORE'):
        assert job._should_run_job()
        job2.idle_task_event.clear()
        assert not job._are_job_dependencies_idle()
        job2.idle_task_event.clear()
        job3.idle_task_event.clear()
        assert not job._are_job_dependencies_idle()
        job2.idle_task_event.set()
        assert not job._are_job_dependencies_idle()
        job3.idle_task_event.set()
        assert job._are_job_dependencies_idle()
    job.stop()


async def test_clear():
    job = AsyncJob(callback)
    job.clear()
    if not os.getenv('CYTHON_IGNORE'):
        assert not job.job_dependencies
        assert not job.job_task
        assert not job.job_periodic_task


async def test_run_stop_run():
    job = AsyncJob(callback, execution_interval_delay=0.5, min_execution_delay=0.2)
    if not os.getenv('CYTHON_IGNORE'):
        with patch.object(job, 'callback', new=AsyncMock()) as mocked_test_job_callback:
            await wait_asyncio_next_cycle()
            mocked_test_job_callback.assert_not_called()
            assert not job.is_started
            await job.run()
            await wait_asyncio_next_cycle()
            mocked_test_job_callback.assert_called_once()
            assert job.is_started
            job.stop()
            await wait_asyncio_next_cycle()
            assert not job.is_started
            mocked_test_job_callback.assert_called_once()
            await job.run()
            await asyncio.sleep(0.7)
            assert job.is_started
            assert mocked_test_job_callback.call_count == 2

            await asyncio.sleep(0.5)
            assert mocked_test_job_callback.call_count == 3
            job.stop()


async def test_run():
    job = AsyncJob(callback, execution_interval_delay=0.5, min_execution_delay=0.2)
    if not os.getenv('CYTHON_IGNORE'):
        with patch.object(job, 'callback', new=AsyncMock()) as mocked_test_job_callback:
            await wait_asyncio_next_cycle()
            mocked_test_job_callback.assert_not_called()
            assert not job.is_started
            await job.run()
            await wait_asyncio_next_cycle()
            mocked_test_job_callback.assert_called_once()
            assert job.is_started

            # delay has not been waited
            await job.run()
            await wait_asyncio_next_cycle()
            mocked_test_job_callback.assert_called_once()
            assert job.is_started

            await asyncio.sleep(0.1)
            mocked_test_job_callback.assert_called_once()

            await asyncio.sleep(0.6)
            assert mocked_test_job_callback.call_count == 2

            await job.run(force=True, wait_for_task_execution=True)
            assert mocked_test_job_callback.call_count == 3

            await wait_asyncio_next_cycle()
            # no periodic trigger yet
            assert mocked_test_job_callback.call_count == 3

            await job.run(force=True, wait_for_task_execution=False)
            # task not yet executed
            assert mocked_test_job_callback.call_count == 3
            await wait_asyncio_next_cycle()
            assert mocked_test_job_callback.call_count == 4

            await asyncio.sleep(0.7)
            # periodic auto trigger
            assert mocked_test_job_callback.call_count == 5

    job.stop()