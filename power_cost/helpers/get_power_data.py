from datetime import datetime, timedelta
from decimal import Decimal

from django.conf import settings
from influxdb import InfluxDBClient


def get_power_data() -> str:
    influx_client = InfluxDBClient(
        host=settings.INFLUX_HOST,
        port=settings.INFLUX_PORT,
        username=settings.INFLUX_USERNAME,
        password=settings.INFLUX_PASSWORD,
        database=settings.INFLUX_DATABASE,
    )
    # TODO Make query more generic and flexible, enumerate returned devices, abstract into
    # data helper model
    data = influx_client.query(
        "SELECT max(value) "
        "FROM kWh WHERE (entity_id =~ /energy_total/) AND "
        "time >= $start_date_time AND time <= $end_date_time "
        "GROUP BY time(1h), friendly_name "
        "fill(linear)",
        bind_params={
            "end_date_time": datetime.today().date().isoformat(),
            "start_date_time": (datetime.today() - timedelta(days=settings.POWER_HISTORY_DAYS))
            .date()
            .isoformat(),
        },
    )
    format_str = "{:<36} {:>12} {:>12}"
    resp = format_str.format("Device Friendly Name", "Energy (KWh)", "Cost (€)") + "\n"
    for (_, tag_data), values in data.items():  # type: ignore
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
            cur_val = Decimal(str(time_max_data["max"]))
            if last_energy_val is None:
                last_energy_val = cur_val
                continue
            total_energy += cur_val - last_energy_val
            # TODO: Check if we are calculating the right value here, whether we need to
            # use the min val for an hour and base our rate off the previous hour etc.
            # Currently using the max val for an hour
            cur_cost = get_rate_from_time(time_max_data["time"]) * (cur_val - last_energy_val)
            total_cost += cur_cost
            # Bump previous energy val tracker
            last_energy_val = cur_val
        total_energy = total_energy.quantize(Decimal("0.001"))
        total_cost = total_cost.quantize(Decimal("0.00"))
        resp += format_str.format(device_name, total_energy, total_cost) + "\n"
    return resp


def get_rate_from_time(time_str: str) -> Decimal:
    """Get rate from time in format:  2023-05-05T08:00:00Z"""
    time = datetime.fromisoformat(time_str)
    hour = time.hour
    rate_type = settings.POWER_TIME_RATE_TYPES[hour]
    return settings.POWER_RATE_TYPE_COSTS[rate_type]
