from abc import abstractmethod
from asyncio import all_tasks, create_task, current_task, gather, get_running_loop
from functools import wraps
from signal import SIGHUP, SIGINT, SIGTERM


class App:
    shutdown_hooks = []
    post_shutdown_hooks = []

    def __init__(self):
        self.shutdown = False
        self._start_coroutine = None

    async def start(self):
        """Start app with this one."""
        self._start_coroutine = current_task()
        loop = get_running_loop()
        for s in (SIGHUP, SIGINT, SIGTERM):
            loop.add_signal_handler(
                s,
                lambda sig=s: create_task(self.graceful_shutdown(sig))
            )
        await self.main()

    @abstractmethod
    async def main(self):
        """Your application entry point."""
        pass

    async def graceful_shutdown(self, signal):
        if self.shutdown:
            return
        self.shutdown = True
        for hook in App.shutdown_hooks:
            hook(self)
        tasks = [t for t in all_tasks()
                 if t not in (current_task(), self._start_coroutine)]

        await gather(*tasks, return_exceptions=True)
        for hook in App.post_shutdown_hooks:
            hook(self)

    @staticmethod
    def worker(method):
        """Entry point to an async worker. Wouldn't start if shutdown has been initiated."""
        @wraps(method)
        async def wrapper(*args, **kwargs):
            if not args[0].shutdown:
                return await method(*args, **kwargs)

        return wrapper

    @classmethod
    def shutdown_hook(cls, hook):
        cls.shutdown_hooks.append(hook)

    @classmethod
    def post_shutdown_hook(cls, hook):
        cls.post_shutdown_hooks.append(hook)
