"""Control IoT device by reading sensor values and writing data to disk."""

from __future__ import annotations
import os
import asyncio
from datetime import datetime
from pypeck.device.configs import DATA_PATH, DATE_FORMAT, load_configs
from pypeck.device.sensor import Sensor


def read_sensors(sensors: list[Sensor]):
  """Read sensor values."""
  data: dict[str, int | None] = {}
  for s in sensors:
    reading = s.read()
    for k in reading:
      if k in data:
        raise KeyError('Duplicate key found!')
    data.update(reading)
  return data


def write_data(data: dict[str, int | None]):
  """Create a data file if none exists and append data to end."""
  time = datetime.now().strftime(DATE_FORMAT)
  values_as_str = [str(v) if v is not None else '' for v in data.values()]
  row = time + ',' + ','.join(values_as_str) + '\n'
  with open(DATA_PATH, 'a') as f:
    f.write(row)


def create_data_file(sensors: list[Sensor]):
  """Create data file if none exists and write column headers, or return most recent data."""

  # taking an initial reading to get header values
  data = read_sensors(sensors)
  headers = data.keys()

  if not os.path.exists(DATA_PATH):
    headers = 'time,' + ','.join(headers) + '\n'
    with open(DATA_PATH, 'w') as f:
      f.write(headers)


def run_device():
  """Run device indefinitely."""
  d = load_configs()
  sensors = [Sensor(s) for s in d.sensors]
  create_data_file(sensors)

  async def run():
    while True:
      await asyncio.sleep(d.update_interval)
      data = read_sensors(sensors)
      write_data(data)

  loop = asyncio.get_event_loop()
  loop.create_task(run())
  loop.run_forever()
