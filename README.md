# async-pokedex

## Version 1. Sequential Implementation

## Version 2. Async with Batching
1. line 43

'''python 
results +=  [await process_pokemon(pokemon, client) for pokemon in batch]
'''
Why is this wrong?  We are awaiting each coroutine inside list comprehension which defeats the purpose of async execution.
Creating coroutines is instant, but awaiting them means that they can only execute sequentially.

'''python 
results +=  await asyncio.gather(*[process_pokemon(pokemon, client) for pokemon in batch])
''' 
So we should not await each individual coroutine, we should gather them and await once.
gather operates on unstarted coroutines and returns an awaitable

RULE: Create all the coroutines first (no await), hand them to gather, then await once.

2. Speedup reason

requests.get DOES NOT reuse connection. so every time it is called it needs to establish new connection.
this is what made our application much slower. So in order to notice the async part doing its job, we 
can add some sleep time to process pokemon (to pretend that there is time consuming operation there).
That way we can clearly see the async working.

3. Sync vs async iterations

def + yield -> for, async def + yield (asyncronous generator) -> async for (and only inside async def)

4. Event Loop Blocking

  Anything that does real work or waits without await-ing:
  - time.sleep()
  - synchronous network: requests.get(), most non-async DB drivers
  - synchronous file I/O: reading/writing large files with plain open()
  - CPU-heavy work: big loops, hashing, image processing, parsing a huge JSON/CSV
The event loop only switches at await; a call that doesn't await (sleep, sync HTTP/DB, file I/O, heavy CPU) holds the single thread and silently freezes all concurrency — so in async code, either use the async version or push
  the blocking call to a thread with asyncio.to_thread.

'''python
  async def task(n):
      print(f"{n} start")
      time.sleep(1)              # ❌ BLOCKING — holds the thread for a full second
      await asyncio.sleep(1)    # ✅ yields control to the loop
      print(f"{n} done")
'''
## Version 3. Async with Semaphore
Slight improvement over batching.
