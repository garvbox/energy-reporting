#! /bin/env python3
import sys
from decimal import Decimal
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
    decimal_precision: int = 6

    class Config:
        env_nested_delimiter = "_"


def main():
    settings = Settings()  # type: ignore
    # getcontext().prec = settings.decimal_precision
    # TODO: Update for Influx V2 - v1.8 servers should support it
    influx_client = InfluxDBClient(**settings.influx.dict())
    # TODO Make query more generic and flexible, enumerate returned devices, abstract into
    # data helper model
    data = influx_client.query(
        "SELECT max(value) "
        "FROM kWh WHERE (entity_id =~ /energy_total/) AND "
        "time >= now() - 30d AND time <= now() "
        "GROUP BY time(1h), friendly_name "
        "fill(linear)",
        # TODO: Fix bind_param injection - getting query date type error
        # bind_params={"num_days": str(settings.num_days) + "d"},
    )
    for (_, tag_data), values in data.items():
        device_name = tag_data["friendly_name"]
        total_energy = Decimal("0.00")
        last_energy_val = Decimal("0.00")
        for time_max_data in values:
            if not time_max_data["max"]:
                # We are using linear interpolation above so this should only happen
                #   when we have values missing from the start of a range. In that case there
                #   is not much we can do with it so we have to just start later
                continue
            cur_val = Decimal(time_max_data["max"])
            if not last_energy_val:
                last_energy_val = cur_val
                continue
            total_energy += cur_val - last_energy_val
        total_energy = total_energy.quantize(Decimal("0.001"))
        print(f"{device_name=} {total_energy}")


if __name__ == "__main__":
    sys.exit(main())
