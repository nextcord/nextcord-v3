# The MIT License (MIT)
# Copyright (c) 2021-present vcokltfre & tag-epic
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

from __future__ import annotations

from asyncio.events import get_event_loop
from collections import defaultdict
from logging import getLogger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

logger = getLogger(__name__)


class Dispatcher:
    def __init__(self):
        self.listeners: dict[Any, list[Any]] = defaultdict(list)
        self.predicates: dict[Any, list[tuple[Any, Any]]] = defaultdict(list)
        self.global_listeners: list[Any] = []
        self.loop = get_event_loop()

    def dispatch(self, event_name: Any, *args):
        logger.debug("Dispatching event %s", event_name)
        # Normal listeners
        for listener in self.listeners[event_name]:
            self.loop.create_task(listener(*args))

        # Predicates
        for predicate_info in self.predicates:
            self.loop.create_task(self._dispatch_predicate(predicate_info, event_name, *args))

        for listener in self.global_listeners:
            self.loop.create_task(listener(event_name, *args))

    async def _dispatch_predicate(self, predicate_info: Any, event_name: Any, *args):
        predicate = predicate_info[0]
        listener = predicate_info[1]
        result = await predicate(*args)

        if result:
            logger.debug("Predicate succeeded, calling listener")
            self.predicates[event_name].remove((predicate, listener))
            self.loop.create_task(listener(*args))  # TODO: Should we just await here?

    def listen(self, event_name: Any = None):
        # TODO: Fix type
        def inner(coro: Any):
            if event_name is None:
                self.global_listeners.append(coro)
            else:
                self.listeners[event_name].append(coro)

        return inner

    def add_predicate(self, event_name: Any, predicate: Any, callback: Any):
        self.predicates[event_name].append((predicate, callback))

    def add_listener(self, event_name: Any, listener: Any):
        if event_name is None:
            self.global_listeners.append(listener)
        else:
            self.listeners[event_name].append(listener)
