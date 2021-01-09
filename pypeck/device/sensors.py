"""See sensor manual.
https://cdn-shop.adafruit.com/product-files/4632/4505_PMSA003I_series_data_manual_English_V2.6.pdf
"""

from __future__ import annotations
import random
import logging
import smbus2  # or just smbus
from pypeck.device.configs import DATE_FORMAT, LOG_PATH, LOG_FORMAT


def configure_sensor_logging():
  """Set up root logger to record sensoring reading errors."""
  root_logger = logging.getLogger()
  formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT)
  file_handler = logging.FileHandler(LOG_PATH)
  file_handler.setFormatter(formatter)
  root_logger.addHandler(file_handler)

  console_handler = logging.StreamHandler()
  console_handler.setFormatter(formatter)
  root_logger.addHandler(console_handler)


configure_sensor_logging()


def read_air():
  """Read I2C data from air sensor."""
  with smbus2.SMBus(1) as bus:
    try:
      data: list[int] = bus.read_i2c_block_data(0x12, 0, 32)
    except OSError:  # couldn't read data -- sensor disconnected?
      logging.warning('Unable to connect to air sensor over I2C')
      return None
    data_dict: dict[str, int] = {}

    # start characters, check sum, error byte
    try:
      assert data[0] == 0x42
      assert data[1] == 0x4d
      assert data[29] == 0
      assert sum(data[:30]) == (data[30] << 8) + data[31]
    except AssertionError:
      logging.warning('Error understanding I2C data read from air sensor.')

    # standard particle reading
    data_dict['pm_1.0'] = (data[4] << 8) + data[5]
    data_dict['pm_2.5'] = (data[6] << 8) + data[7]
    data_dict['pm_10'] = (data[8] << 8) + data[9]

    # atmospheric environment reading
    data_dict['pm_atmos_1.0'] = (data[10] << 8) + data[11]
    data_dict['pm_atmos_2.5'] = (data[12] << 8) + data[13]
    data_dict['pm_atmos_10'] = (data[14] << 8) + data[15]

    # reading beyond threshold
    data_dict['n_beyond_0.3'] = (data[16] << 8) + data[17]
    data_dict['n_beyond_0.5'] = (data[18] << 8) + data[19]
    data_dict['n_beyond_1.0'] = (data[20] << 8) + data[21]
    data_dict['n_beyond_2.5'] = (data[22] << 8) + data[23]
    data_dict['n_beyond_5.0'] = (data[24] << 8) + data[25]
    data_dict['n_beyond_10'] = (data[26] << 8) + data[27]

  return data_dict


def read_random(prev_reading: int | None = None):
  """Create random data for testing."""
  if prev_reading is None:
    r = random.randint(0, 255)
  else:
    r = prev_reading + random.randint(-3, 3)
    r = max(min(r, 255), 0)  # clipping
  return {'random': r}