from apscheduler.schedulers.asyncio import AsyncIOScheduler
import threading
import asyncio
import time
import os
import importlib
from utils import config
import head
# import lab.petals

# # lab.petals.load_model()

# This is the main loop for the entire machine
@asyncio.coroutine
async def main(loop):

    focus = os.environ["FOCUS"]

    scheduler = AsyncIOScheduler()
    scheduler.add_job(head.loader, args=[focus], trigger="interval", minutes=30)
    scheduler.start()

    tasks = {}

    head.ai = await head.loader(focus)

    allowed_services = [
        "source",
        "telegram",
        "telegraph",
        "reddit",
        "discord",
        "twitch",
        "twitter",
        "petals"
    ]

    while True:
        # Prune completed tasks
        for task in tasks.copy():
            if tasks[task].done() or tasks[task].cancelled():
                del tasks[task]

        # Get configs, create tasks, and append to task queue
        for service in config:
            if service not in allowed_services:
                continue
            if service not in tasks:
                module = importlib.import_module(f"lab.{service}")
                task = loop.create_task(getattr(module, "orchestrate")(config[service]))
                task.set_name(service)
                tasks[task.get_name()] = task

        await asyncio.sleep(66.6)


# Start the main loop in a thread
def loop_in_thread(loop):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main(loop))

t = None
while True:
    time.sleep(5)
    if not t or not t.is_alive():
        loop = asyncio.get_event_loop()
        t = threading.Thread(None, loop_in_thread, args=(loop,), daemon=True)
        t.start()