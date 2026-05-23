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
from datetime import datetime, timezone
import logging
from pythonjsonlogger.json import JsonFormatter

EXCLUDED_KEYS = { 'name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 'filename', 'module', 'exc_info',
                  'exc_text', 'stack_info', 'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
                  'taskName', 'thread', 'threadName', 'processName', 'process', 'message', 'asctime',
                  'trail_id', 'service' }


class ConsoleFormatter(logging.Formatter):

    def format(self, record):
        base_message = super().format(record)

        extras = []

        for key, value in record.__dict__.items():
            if key not in EXCLUDED_KEYS:
                extras.append(f"{key}={value}")

        if extras:
            return f"{base_message} {' '.join(extras)}"

        return base_message

    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, tz=timezone.utc)

        return dt.isoformat(timespec='milliseconds').replace('+00:00', 'Z')


class ISOJsonFormatter(JsonFormatter):

    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, tz=timezone.utc)

        return dt.isoformat(timespec='milliseconds').replace('+00:00', 'Z')
