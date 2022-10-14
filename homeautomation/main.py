import contextlib
import math
import os
import aiohttp
import asyncio
import pysmartthings
import datetime
from typing import List
from time import sleep
import inspect
import sys
from pprint import pprint
from typing_extensions import DefaultDict

token = os.environ["SMARTTHINGS_PERSONAL_ACCESS_TOKEN"]
now = datetime.datetime.now()
loop = asyncio.new_event_loop()

once_token = 0

example_device_values = {}


class DeviceValues:
    def __init__(self, values):
        self.online = values["DeviceWatch-DeviceStatus"]  # ex: 'offline'
        # 'DeviceWatch-Enroll': None,
        self.check_interval = values["checkInterval"]  # ex: 60
        self.color = values["color"]  # ex: None
        self.color_temperature = values["colorTemperature"]  # ex: 6500
        self.level = values["level"]  # ex: 100
        self.saturation = values["saturation"]  # ex: 100
        self.switch = values["switch"]  # ex : 'on'
        # 'healthStatus': None,
        # 'hue': 0,


"""
'_api': <pysmartthings.api.Api object at 0x7f255f52cdc0>,
'_capabilities'
'_components': {},
'_device_id': 'b3753858-e2d7-46a7-84e2-8dcab0645348',
'_device_type_id': '479a0628-421e-426c-914d-3f16dacd3095',
'_device_type_name': 'ZigBee RGBW Bulb',
'_device_type_network': 'ZIGBEE',
'_label': 'Sengled Multicolor [office]',
'_location_id': '391a436f-dd31-4876-9fcf-30bbe6dc64f0',
'_name': 'Sengled Multicolor',
'_room_id': '3c001d16-6f00-4393-ad5e-8184e5035545',
'_status': <pysmartthings.device.DeviceStatus object at 0x7f255ef1e1d0>,
                                                      '_type': 'DTH'}
"""


async def configure_vacation(device: pysmartthings.DeviceEntity, temperature, level):
    await device.status.refresh()
    values = DeviceValues(values=device.status.values)

    # new logic for on daytime, off nighttime
    _now_hour = datetime.datetime.now()

    if get_time(8) < _now_hour < get_time(23):
        pass
    else:
        await device.switch_off()
        return

    await device.set_color_temperature(temperature=temperature)
    await device.set_level(level=level)
    print(
        device.label,
        values.online,
        values.switch,
        values.color_temperature,
        values.level,
    )


async def configure(device: pysmartthings.DeviceEntity, temperature, level):
    await device.status.refresh()
    values = DeviceValues(values=device.status.values)

    # new logic for on daytime, off nighttime
    _now_hour = datetime.datetime.now()

    # skip if off
    if values.online == "offline":
        return
    if values.switch == "off":
        return

    await device.set_color_temperature(temperature=temperature)
    await device.set_level(level=level)

    # report
    print(
        device.label,
        values.online,
        values.switch,
        values.color_temperature,
        values.level,
    )


async def main():
    async with aiohttp.ClientSession() as session:
        api = pysmartthings.SmartThings(session, token)
        all_devices: List[pysmartthings.DeviceEntity] = await api.devices()
        devices: List[pysmartthings.DeviceEntity] = [
            d for d in all_devices if "colorTemperature" in d._capabilities
        ]

        print_once([d.label for d in devices])
        schedule = get_schedule()
        time = schedule[get_time_of_day(schedule)]
        temperature = time["temperature"]
        level = time["level"]
        await asyncio.gather(
            *[configure(device, temperature, level) for device in devices]
        )
        # await asyncio.gather(*[d.set_color(hue=0, saturation=100) for d in devices])


def run(loop):
    loop.run_until_complete(main())


def seconds(t: datetime.datetime):
    return t.timestamp()


def test_run():
    print("\n")
    run(loop)


def get_time_of_day(schedule):
    now = datetime.datetime.now()
    times = list(schedule.keys())
    for t in times[::-1]:
        if now > t:
            return t
    return times[-1]


def temp(value):
    _min = 2200  # 2200
    _max = 6500  # 6500
    actual_temp = math.floor(((value - _min) / (_max - _min) * 10000))
    if actual_temp < 1:
        actual_temp = 1
    if actual_temp > 10000:
        actual_temp = 10000
    return actual_temp


def test_interpolate():
    assert interpolate(t1=1, t2=3, v1=1, v2=3, tx=2) == 2


def interpolate(t1, t2, v1, v2, tx):
    # y = mx + b
    m = (v2 - v1) / (t2 - t1)
    b = v1 - m * t1
    y = m * tx + b
    return y


def get_schedule():
    # temperatures from CREE
    # temperature can go from 2200 to 6500

    candle_light = temp(2200)
    soft_white = temp(2700)
    bright_white = temp(3000)
    neutral_white = temp(3500)
    cool_white = temp(4000)
    daylight = temp(5000)
    sun_light = temp(6000)

    # times
    sunrise = get_time(6)
    mid_morning = get_time(9)
    noon = get_time(12)
    afternoon = get_time(15)
    sunset = get_time(17)
    bedtime = get_time(22)

    # schedule
    schedule = {
        sunrise: {"temperature": soft_white, "level": 90},
        mid_morning: {"temperature": soft_white, "level": 90},
        noon: {"temperature": soft_white, "level": 100},
        afternoon: {"temperature": soft_white, "level": 100},
        sunset: {"temperature": soft_white, "level": 50},
        bedtime: {"temperature": candle_light, "level": 15},
    }
    return schedule


def get_time(hour):
    datetime.datetime.now()
    return now.replace(**{"hour": hour}, **{"minute": 0, "second": 0, "microsecond": 0})


def print_once(data):
    global once_token
    if once_token:
        pass
    else:
        pprint(data)
        once_token = 1


if __name__ == "__main__":
    # while True:
    try:
        print("---")
        print(f"{datetime.datetime.now()} Starting")
        run(loop)
        print(f"{datetime.datetime.now()} SUCCESS")
    except Exception as e:
        print(f"{datetime.datetime.now()} FAILURE")
        print(e)
        pass
        # sleep(30)
