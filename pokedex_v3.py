import json
import time

import httpx
import asyncio

LIST_URL = 'https://pokeapi.co/api/v2/pokemon'
BUDGET = 200
OUTPUT = 'pokedex_sequential.jsonl'


async def fetch_page(url, offset, limit, client):
        return (await client.get(url, params={'offset': offset, 'limit': limit})).json()


async def fetch(client):
    offset = 0
    while True:
        res =  await fetch_page(LIST_URL, offset, 100, client)
        if not res['results']:
            break
        yield  res
        offset += 100


async def process_pokemon(pokemon, client, sem):
    async with sem:
        details = await client.get(pokemon['url'])
        moves = details.json()['moves']
        strong_moves = []
        for move in moves:
            name = move['move']['name']
            if move['version_group_details'][0]['level_learned_at'] >= 20:
                strong_moves.append(name)
        await asyncio.sleep(0.2)
        return {'name': pokemon['name'], 'strong_moves': strong_moves}


async def run(client, budget=BUDGET):
    sem = asyncio.Semaphore(20)
    results = []
    async for page in fetch(client):
        results += await asyncio.gather(*[process_pokemon(pokemon, client, sem) for pokemon in page['results']])
        if len(results) >= budget:
            return results
    return results


async def main():
    async with httpx.AsyncClient() as client:
        return await run(client)

if __name__ == '__main__':
    start = time.perf_counter()
    results = asyncio.run(main())                      # time ONLY the network work
    elapsed = time.perf_counter() - start

    with open(OUTPUT, 'w') as f:         # write after timing
        for r in results:
            f.write(json.dumps(r) + '\n')

    print(f"{len(results)} pokemon in {elapsed:.2f}s "
          f"({elapsed / len(results) * 1000:.0f} ms each)")
