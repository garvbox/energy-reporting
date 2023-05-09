#! /bin/env python3
import sys
from typing import Optional

from influxdb import InfluxDBClient
from pydantic import BaseModel, BaseSettings


class InfluxConnectionSettings(BaseModel):
    host: str = "localhost"
    port: int = 8086
    username: Optional[str] = None
    password: Optional[str] = None
    database: str


class Settings(BaseSettings):
    influx: InfluxConnectionSettings
    num_days: int = 1

    class Config:
        env_nested_delimiter = "_"


def main():
    settings = Settings()  # type: ignore
    # TODO: Update for Influx V2 - v1.8 servers should support it
    influx_client = InfluxDBClient(**settings.influx.dict())
    # TODO Make query more generic and flexible, enumerate returned devices, abstract into
    # data helper model
    data = influx_client.query(
        f'SELECT max("value") '
        f'FROM "kWh" WHERE ("entity_id" =~ /energy_total/) AND '
        f"time >= now() - {settings.num_days}d and time <= now() "
        f'GROUP BY time(1h), "friendly_name"'
    )
    for (_, tag_data), values in data.items():
        device_name = tag_data["friendly_name"]
        total_energy = 0
        last_energy_val = 0
        for time_max_data in values:
            if not time_max_data["max"]:
                # TODO: None values are missing data for that time range, we will likely need to
                # handle these using longer-range interpolation and tracking of last-known
                # time-value pairs.
                continue
            if not last_energy_val:
                last_energy_val = time_max_data["max"]
                continue
            total_energy += round(time_max_data["max"] - last_energy_val, 3)

        print(f"{device_name=} {total_energy=}")


if __name__ == "__main__":
    sys.exit(main())
