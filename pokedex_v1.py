import json
import time

import requests

LIST_URL = 'https://pokeapi.co/api/v2/pokemon'
BUDGET = 50
OUTPUT = 'pokedex_sequential.jsonl'


def fetch_page(url, offset, limit):
        return requests.get(url, params={'offset': offset, 'limit': limit}).json()

def fetch():
    offset = 0
    while True:
        res =  fetch_page(LIST_URL, offset, 100)
        if not res['results']:
            break
        yield  res
        offset += 100

def process_pokemon(pokemon):
    details = requests.get(pokemon['url']).json()
    moves = details['moves']
    strong_moves = []
    for move in moves:
        name = move['move']['name']
        if move['version_group_details'][0]['level_learned_at'] >= 20:
            strong_moves.append(name)
    return {'name': pokemon['name'], 'strong_moves': strong_moves}

def run(budget=BUDGET):
    results = []
    for page in fetch():
        for pokemon in page['results']:
            results.append(process_pokemon(pokemon))
            if len(results) >= budget:
                return results
    return results

if __name__ == '__main__':
    start = time.perf_counter()
    results = run()                      # time ONLY the network work
    elapsed = time.perf_counter() - start

    with open(OUTPUT, 'w') as f:         # write after timing
        for r in results:
            f.write(json.dumps(r) + '\n')

    print(f"{len(results)} pokemon in {elapsed:.2f}s "
          f"({elapsed / len(results) * 1000:.0f} ms each)")
