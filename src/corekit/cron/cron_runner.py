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
from typing import Callable

logger = logging.getLogger(__name__)

class CronRouter:

    def __init__(self):
        self._handlers: dict[str, Callable] = { }

    def task(self, job_name: str):
        def decorator(fn):
            self._handlers[job_name] = fn
            return fn

        return decorator

    def handlers(self) -> dict[str, Callable]:
        return self._handlers

class CronRunner:

    def __init__(self):
        self._handlers: dict[str, Callable] = { }

    @property
    def jobs(self) -> list[str]:
        return list(self._handlers.keys())

    def register_task_router(self, router: CronRouter):
        self._handlers.update(router.handlers())

        return self

    def execute(self, job_name: str, *args, **kwargs):
        handler = self._handlers.get(job_name)

        logger.info('Starting job', extra={ 'job_name': job_name })

        if handler is None:
            logger.error('Unknown job', extra={ 'job_name': job_name })
            return

        result = handler(*args, **kwargs)

        logger.info('Job completed', extra={ 'job_name': job_name, 'result': result })