import asyncio
import aiohttp
from more_itertools import chunked
from models import engine, Session, Base, SwapiPeople
import json
import requests

CHUNK_SIZE = 10


def count_people():
    response = requests.get(f"https://swapi.dev/api/people/").json()
    count = response["count"]
    return count


async def get_people(session, people_id):
    async with session.get(f"https://swapi.dev/api/people/{people_id}") as response:
        json_data = await response.json()
        return json_data


async def paste_to_db(results):

    for record in results:
        list_films = []
        list_starships = []
        list_vehicles = []
        list_homeworld = []
        list_species = []
        if type(record['films']) != list:
            response = requests.get(f"{record['films']}").json()
            list_films.append(response["title"])
        else:
            for film in record['films']:
                response = requests.get(f"{film}").json()
                list_films.append(response["title"])

        if type(record['starships']) != list:
            response = requests.get(f"{record['starships']}").json()
            list_starships.append(response["name"])
        else:
            for film in record['starships']:
                response = requests.get(f"{film}").json()
                list_starships.append(response["name"])

        if type(record['vehicles']) != list:
            response = requests.get(f"{record['vehicles']}").json()
            list_vehicles.append(response["name"])
        else:
            for film in record['vehicles']:
                response = requests.get(f"{film}").json()
                list_vehicles.append(response["name"])

        if type(record['homeworld']) != list:
            response = requests.get(f"{record['homeworld']}").json()
            list_homeworld.append(response["name"])
        else:
            for film in record['homeworld']:
                response = requests.get(f"{film}").json()
                list_homeworld.append(response["name"])

        if type(record['species']) != list:
            response = requests.get(f"{record['species']}").json()
            list_species.append(response["name"])
        else:
            for film in record['species']:
                response = requests.get(f"{film}").json()
                list_species.append(response["name"])

        async with Session() as session:
            session.add(SwapiPeople(name=record.get('name'), birth_year=record.get('birth_year'),
                                    eye_color=record.get('eye_color'), gender=record.get('gender'),
                                    hair_color=record.get('hair_color'), height=record.get('height'),
                                    mass=record.get('mass'), skin_color=record.get('skin_color'),
                                    films=f"{list_films}", starships=f"{list_starships}",
                                    vehicles=f"{list_vehicles}", homeworld=f"{list_homeworld}",
                                    species=f"{list_species}"))
            await session.commit()


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session = aiohttp.ClientSession()
    coros = []
    for i in range(1, count_people()+1):
        coroutine = get_people(session, i)
        coros.append(coroutine)
    for coros_chunk in chunked(coros, CHUNK_SIZE):
        results = await asyncio.gather(*coros_chunk)
        asyncio.create_task(paste_to_db(results))
    print("OK")

    await session.close()
    set_task = asyncio.all_tasks()
    for task in set_task:
        if task != asyncio.current_task():
            await task

asyncio.get_event_loop().run_until_complete(main())
