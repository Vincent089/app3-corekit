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
import time
from functools import wraps
from corekit.utils import calc_duration
from corekit.execptions import DomainError

logger = logging.getLogger(__name__)

def log_service_call(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        start = time.time()

        class_name = args[0].__class__.__name__
        func_name = fn.__name__

        logger.info(
                f'Entering service method',
                extra={
                    'class': class_name,
                    'func': func_name,
                }
        )

        try:
            result = fn(*args, **kwargs)
            duration = calc_duration(start)

            logger.info(
                    f'Service method completed',
                    extra={
                        'class': class_name,
                        'func': func_name,
                        'duration_ms': duration,
                    }
            )

            return result

        except DomainError as e:
            duration = calc_duration(start)

            logger.warning(
                    f'Service method exited',
                    extra={
                        'exception': e.__class__.__name__,
                        'error': str(e),
                        'class': class_name,
                        'func': func_name,
                        'duration_ms': duration,
                    }
            )
            raise

        except Exception as e:
            duration = calc_duration(start)

            logger.exception(
                    f'Service method failed',
                    extra={
                        'exception': e.__class__.__name__,
                        'error': str(e),
                        'class': class_name,
                        'func': func_name,
                        'duration_ms': duration,
                    }
            )
            raise

    return wrapper
