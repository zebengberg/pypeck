"""Validate configs with pydantic. Sensor fields are chosen so that
d -> Device(**d.dict()) is an involution."""


# cannot use __future__ annotations with pydantic
from typing import List, Union, Dict
from pydantic import BaseModel, validator


class AirSensorConfigs(BaseModel):
  sensor_type: str = 'air'
  i2c_address: int

  @validator('sensor_type')
  def check_sensor_type(cls, value: str):
    assert value == 'air'
    return value


class IRSensorConfigs(BaseModel):
  sensor_type: str = 'ir'
  bcm_pin: int

  @validator('sensor_type')
  def check_sensor_type(cls, value: str):
    assert value == 'ir'
    return value


class RandomSensorConfigs(BaseModel):
  sensor_type: str = 'random'
  header: str

  @validator('sensor_type')
  def check_sensor_type(cls, value: str):
    assert value == 'random'
    return value


class DeviceConfigs(BaseModel):
  """A Class holding configuration fields of the device."""
  name: str
  location: str
  sensors: List[Union[AirSensorConfigs, IRSensorConfigs, RandomSensorConfigs]]
  plot_axes: Dict[str, List[str]]
  update_interval: int

  @validator('plot_axes')
  def check_plot_axes(cls, value: Dict[str, List[str]]):
    assert len(value) in [1, 2]  # can only handle 1 or 2 y-axes currently
    return value


def random_configs():
  """Return a device with a random sensor."""
  s1 = RandomSensorConfigs(sensor_type='random', header='random1')
  s2 = RandomSensorConfigs(sensor_type='random', header='random2')
  s3 = RandomSensorConfigs(sensor_type='random', header='random3')
  d = DeviceConfigs(
      name='random sensor',
      location='table',
      sensors=[s1, s2, s3],
      plot_axes={'random reading': ['random1', 'random2', 'random3']},
      update_interval=5)
  assert d == DeviceConfigs(**d.dict())
  return d


def example_configs():
  """Return an example of valid configs as json."""
  s1 = AirSensorConfigs(sensor_type='air', i2c_address=0x12)
  s2 = IRSensorConfigs(sensor_type='ir', bcm_pin=17)
  d = DeviceConfigs(
      name='razzy',
      location='table',
      sensors=[s1, s2],
      plot_axes={'micrograms / cubic meter': ['pm_2.5', 'pm_10'],
                 'on-off': ['ir_state']},
      update_interval=1)
  assert d == DeviceConfigs(**d.dict())
  return d
