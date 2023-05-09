#! /bin/env python3
import sys
from datetime import datetime
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
    decimal_precision: int = 6
    start_date: str
    end_date: str

    class Config:
        env_nested_delimiter = "_"


# TODO: Store temp hard-coded rates elsewhere
TIME_RATE_TYPES = {
    0: "night",
    1: "night",
    2: "night",
    3: "night",
    4: "night",
    5: "night",
    6: "night",
    7: "night",
    8: "day",
    9: "day",
    10: "day",
    11: "day",
    12: "day",
    13: "day",
    14: "day",
    15: "day",
    16: "day",
    17: "peak",
    18: "peak",
    19: "day",
    20: "day",
    21: "day",
    22: "day",
    23: "day",
}
RATE_TYPE_COSTS = {"day": Decimal("0.3095"), "night": Decimal("0.2008"), "peak": Decimal("0.3911")}


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
        "time >= $start_date_time AND time <= $end_date_time "
        "GROUP BY time(1h), friendly_name "
        "fill(linear)",
        bind_params={"start_date_time": settings.start_date, "end_date_time": settings.end_date},
    )
    for (_, tag_data), values in data.items():
        device_name = tag_data["friendly_name"]
        total_energy = Decimal("0.00")
        total_cost = Decimal("0.00")
        last_energy_val = None
        for time_max_data in values:
            if time_max_data["max"] is None:
                # We are using linear interpolation above so this should only happen
                #   when we have values missing from the start of a range. In that case there
                #   is not much we can do with it so we have to just start later
                continue
            cur_val = Decimal(time_max_data["max"])
            if last_energy_val is None:
                last_energy_val = cur_val
                continue
            total_energy += cur_val - last_energy_val
            cur_cost = get_rate(time_max_data["time"]) * (cur_val - last_energy_val)
            total_cost += cur_cost
        total_energy = total_energy.quantize(Decimal("0.001"))
        total_cost = total_cost.quantize(Decimal("0.00"))
        print(f"{device_name=} {total_energy=} {total_cost=}")


def get_rate(time_str: str) -> Decimal:
    """Get rate from time in format:  2023-05-05T08:00:00Z"""
    time = datetime.fromisoformat(time_str)
    hour = time.hour
    rate_type = TIME_RATE_TYPES[hour]
    return RATE_TYPE_COSTS[rate_type]


if __name__ == "__main__":
    sys.exit(main())
