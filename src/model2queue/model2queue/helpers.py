import asyncio


def run_in_main_loop(func, *args, **kwargs):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:  # 'RuntimeError: There is no current event loop...'
        loop = None
    if loop and loop.is_running():
        tsk = loop.create_task(func(*args, **kwargs))
        tsk.add_done_callback(
            lambda t: print(
                f"Task done with result={t.result()}  << return val of main()"
            )
        )
    else:
        asyncio.run(func(*args, **kwargs))
