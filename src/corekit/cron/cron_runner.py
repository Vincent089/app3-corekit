#   -----------------------------------------------------------------------------
#  Copyright (c) 2026. Vincent Corriveau (vincent.corriveau89@gmail.com)
#
#  Licensed under the MIT License. You may obtain a copy of the License at
#  https://opensource.org/licenses/MIT
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  -----------------------------------------------------------------------------
import logging
import uuid
from typing import Callable

from corekit.context import trail_id_var

logger = logging.getLogger(__name__)

class CronRouter:

    def __init__(self):
        self._handlers: dict[str, Callable] = { }

    def register(self, stream_key: str):
        def decorator(fn):
            self._handlers[stream_key] = fn
            return fn

        return decorator

    def handlers(self) -> dict[str, Callable]:
        return self._handlers

class CronRunner:

    def __init__(self):
        self._handlers: dict[str, Callable] = { }

    @property
    def cron_jobs(self) -> list[str]:
        return list(self._handlers.keys())

    def include_router(self, router: CronRouter):
        self._handlers.update(router.handlers())

        return self

    def execute(self, job_name: str):
        handler = self._handlers.get(job_name)
        trail_id_var.set(str(uuid.uuid4()))

        logger.info('Starting cron', extra={ 'job_name': job_name })

        if handler is None:
            logger.error('Unknown cron job', extra={ 'job_name': job_name })
            return

        result = handler()

        logger.info('Cron completed', extra={ 'job_name': job_name, 'result': result })