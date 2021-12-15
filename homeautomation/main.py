import os
import aiohttp
import asyncio
import pysmartthings
import datetime
from typing import List
from time import sleep

token = os.environ['SMARTTHINGS_PERSONAL_ACCESS_TOKEN']
now = datetime.datetime.now()
loop = asyncio.get_event_loop()

async def configure(device: pysmartthings.DeviceEntity, temperature, level):
    await device.set_color_temperature(temperature=temperature)
    await device.set_level(level=level)


async def main():
    async with aiohttp.ClientSession() as session:
        api = pysmartthings.SmartThings(session, token)
        devices: List[pysmartthings.DeviceEntity] = await api.devices()
        schedule = get_schedule()
        time = schedule[get_tod(schedule)]
        temperature = time["temperature"]
        level = time["level"]
        await asyncio.gather(
            *[
                configure(device, temperature, level) for device in devices
            ]
        )
        # await asyncio.gather(*[d.set_color(hue=0, saturation=100) for d in devices])
    print(f"{datetime.datetime.now()} SUCCESS")


def run(loop):
    loop.run_until_complete(main())


def test_run():
    print("\n")
    run()


def get_tod(schedule):
    now = datetime.datetime.now()
    times = list(schedule.keys())
    for t in times[::-1]:
        if now > t:
            return t
    return times[-1]


def get_schedule():
    sunrise = get_time(6)
    mid_morning = get_time(9)
    noon = get_time(12)
    afternoon = get_time(15)
    sunset = get_time(20)
    bedtime = get_time(22)
    # temperature can go from 2200 to 6500
    return {
        sunrise: {"temperature": 3000, "level": 90},
        mid_morning: {"temperature": 4600, "level": 100},
        noon: {"temperature": 6500, "level": 100},
        afternoon: {"temperature": 4600, "level": 100},
        sunset: {"temperature": 2700, "level": 100},
        bedtime: {"temperature": 2200, "level": 10},
    }


def get_time(hour):
    datetime.datetime.now()
    return now.replace(**{"hour": hour}, **{"minute": 0, "second": 0, "microsecond": 0})


if __name__ == '__main__':
    while True:
        try:
            run(loop)
        except Exception as e:
            print(f"{datetime.datetime.now()} FAILURE")
            print(e)
            pass
        sleep(15)
