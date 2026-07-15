#   -----------------------------------------------------------------------------
#  Copyright (c) 2026. Vincent Corriveau (vincent.corriveau89@gmail.com)
#
#  Licensed under the MIT License. You may obtain a copy of the License at
#  https://opensource.org/licenses/MIT
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an 'AS IS' BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  -----------------------------------------------------------------------------
import time
import logging
import uuid
import redis
from typing import Callable
from corekit.context import trail_id_var, user_id_var
from corekit.execptions import AlreadyExistsError

logger = logging.getLogger(__name__)


class StreamRouter:

    def __init__(self):
        self._handlers: dict[str, Callable] = { }

    def register(self, stream_key: str):
        def decorator(fn):
            self._handlers[stream_key] = fn
            return fn

        return decorator

    def handlers(self) -> dict[str, Callable]:
        return self._handlers


class RedisStreamConsumer:

    def __init__(self, host, port, consumer_group, consumer_name, decode_responses=True):
        self.consumer_group = consumer_group
        self.consumer_name = consumer_name
        self.r = redis.Redis(host=host, port=port, decode_responses=decode_responses)
        self.r.ping() # to validate connection with Redis immediately
        self._handlers: dict[str, Callable] = { }

    @property
    def stream_keys(self) -> list[str]:
        return list(self._handlers.keys())

    def include_router(self, router: StreamRouter):
        self._handlers.update(router.handlers())

        return self

    def process_message(self, stream_key: str, msg_id: str, data: dict):
        handler = self._handlers.get(stream_key)

        logger.info('Processing message', extra={ 'msg_id': msg_id, 'data': data })

        if handler is None:
            logger.warning(f'No handler registered for stream "{stream_key}", skipping')
            return

        result = handler(data)

        logger.info('Message processed', extra={ 'result': result })

    def ensure_consumer_group(self):
        """
        Create the consumer group if it doesn't exist.
        """
        for stream_key in self.stream_keys:
            try:
                # id='0' = starts from the very beginning of the stream. id='$' to start from latest only
                self.r.xgroup_create(stream_key, self.consumer_group, id='0', mkstream=True)
                logger.info('Consumer group created', extra={ 'consumer_group': self.consumer_group })

            except redis.exceptions.ResponseError as exc:
                if 'BUSYGROUP' in str(exc):
                    logger.debug('Consumer group already exists', extra={ 'consumer_group': self.consumer_group })
                else:
                    raise exc

    def recover_pending(self):
        """
        Reclaim and reprocess any messages that were delivered to the consumer (or consumers in the group)
        but never acknowledged.
        """
        logger.info('Checking PEL for unacknowledged messages')

        for stream_key in self.stream_keys:
            while True:
                pending = self.r.xpending_range(
                        stream_key,
                        self.consumer_group,
                        min='-',
                        max='+',
                        count=100,
                )

                if not pending:
                    logger.info('PEL is empty, no recovery needed', extra={ 'stream_key': stream_key })
                    break

                logger.warning('PEL not empty, recovering', extra={ 'pel_len': len(pending) })

                for entry in pending:
                    msg_id = entry['message_id']

                    claimed = self.r.xclaim(
                            stream_key,
                            self.consumer_group,
                            self.consumer_name,
                            min_idle_time=0,
                            message_ids=[msg_id],
                    )

                    for _, data in claimed:
                        self._process_and_ack(stream_key, msg_id, data)

        logger.info('PEL recovery complete')

    def _process_and_ack(self, stream_key: str, msg_id: str, data: dict):
        """
        Process a single message. Only ack on success.
        A failed message is left in the PEL intentionally.
        """
        trail_id = data.pop('_trail_id', str(uuid.uuid4()))
        user_id = data.pop('_user_id', 'unknown')

        trail_id_var.set(trail_id)
        user_id_var.set(user_id)

        try:
            self.process_message(stream_key, msg_id, data)
            self.r.xack(stream_key, self.consumer_group, msg_id)
            logger.debug('Acked', extra={ 'msg_id': msg_id })

        except AlreadyExistsError as exc:
            logger.warning('Message data already process, removing from PEL', extra={ 'msg_id': msg_id, 'err': exc })
            self.r.xack(stream_key, self.consumer_group, msg_id)

        except Exception as exc:
            logger.error('Failed to process message, leaving in PEL', extra={ 'msg_id': msg_id, 'err': exc })

    def start_listening(self):
        """
        Main loop to listen to events
        """

        self.ensure_consumer_group()
        self.recover_pending()

        logger.info(f'Stream listener started', extra={ 'consumer_group': self.consumer_group })

        # '>' means: only messages not yet delivered to any consumer in the group.
        read_spec = { key: '>' for key in self.stream_keys }

        while True:
            try:
                entries = self.r.xreadgroup(
                        self.consumer_group,
                        self.consumer_name,
                        read_spec,
                        count=10,  # messages per XREADGROUP call
                        block=2000,  # block up to 2s when stream is idle
                )

                if not entries:
                    continue

                for stream_key, messages in entries:
                    for msg_id, data in messages:
                        self._process_and_ack(stream_key, msg_id, data)

            except redis.RedisError as exc:
                logger.error('Redis error in consume loop — retrying in 5s', extra={ 'err': exc })
                time.sleep(5)

class RedisStreamProducer:

    def __init__(self, host, port, consumer_group, consumer_name, decode_responses=True):
        self.consumer_group = consumer_group
        self.consumer_name = consumer_name
        self.r = redis.Redis(host=host, port=port, decode_responses=decode_responses)
        self.r.ping() # to validate connection with Redis immediately
        self._handlers: dict[str, callable] = { }

    def emit_event(self, stream_key: str, payload: dict):
        """
        Emit event to the stream.
        XADD is atomic — either the entry is written to AOF and the stream, or it isn't.
        """
        logger.info('Emitting event.', extra={ 'stream_key': stream_key, 'payload': payload })

        message = {
            **payload,
            '_trail_id': trail_id_var.get(),
            '_user_id': user_id_var.get(),
        }

        msg_id = self.r.xadd(
                stream_key,
                message,
                maxlen=10000, # Size maxlen to cover worst-case consumer downtime x producer emit rate.
                approximate=True,  # '~' trim — more CPU-efficient, slightly loose upper bound
        )

        logger.info('Message emitted', extra={ 'msg_id': msg_id, 'stream_key': stream_key, 'payload': payload })
        return msg_id
