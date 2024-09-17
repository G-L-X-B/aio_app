# aio_app
Asyncio app with graceful shutdown and pre-/post-shutdown hooks.

## Installation
Submodule it or whatever, then import.

## Usage
```python
from asyncio import run
from json import dumps, loads

from aio_app import App
from websockets import connect


class Bpp:
    def __init__(self):
        super().__init__()
        # stuff

    # This one will only start if shutdown has not been initiated
    @App.worker
    async def foo(self, bar):
        # buzzing around
        pass

    # You have to redefine this, the app will use this method as an entry point
    async def main(self):
        uri = 'wss://some.portal/api/data'
        ws = await connect(uri)
        await ws.send(dumps(dict(method='some_api_method')))
        async for message in ws:
            message = loads(message)
            await foo(message)
            if self.shutdown:
                kms() # right now you need to watch for shutdown for yourself,
                      # I might change this later in favour of exception
                      # on faulty worker start
        await ws.close()
        
    # These will be called when shutdown is initiated
    # Ordering is a thing
    @App.shutdown_hook
    def say_goodbye(self):
        print('See you, space cowboy...')
        
    @App.shutdown_hook
    def pray(self):
        print('Amen')
    
    # And this will be called when all the workers have stopped
    @App.post_shutdown_hook
    def bury(self):
        print('Shovels go brrrrrrr')
```