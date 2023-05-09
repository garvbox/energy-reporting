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

    class Config:
        env_nested_delimiter = "_"


def main():
    settings = Settings()  # type: ignore
    # TODO: Update for Influx V2 - v1.8 servers should support it
    influx_client = InfluxDBClient(**settings.influx.dict())
    # TODO Make query more generic and flexible, enumerate returned devices, abstract into
    # data helper model
    data = influx_client.query(
        'SELECT max("value") '
        'FROM "kWh" WHERE ("entity_id" =~ /energy_total/) AND time >= now() - 1d and time <= now() '
        'GROUP BY time(1h), "friendly_name" fill(linear)'
    )
    # TODO: Do something a bit more useful with the data!!
    for k, el in data.items():
        print(k)
        for val in el:
            print(val)


if __name__ == "__main__":
    sys.exit(main())
