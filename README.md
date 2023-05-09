# Energy-Reporting

Home energy usage reporting tools

## Running

These tools are intended to be used with poetry to manage dependencies automatically. See
installation instructions [here](https://python-poetry.org/docs/#installation).

All examples below are using poetry to run the scripts, and this is likely to be converted to
a web server or Lambda in future where poetry will be needed for depencency management on ephemeral
environments.

## Development

Pre-commit hooks are provided for ensuring consistent style. Black is used for auto-formatting, it
is highly reccomended to enable format on save in your editor with black so that this is automatically
dealt with.

Install pre-commit hooks (ensure you have installed poetry first):
`poetry run pre-commit install`

## Tools

Provided scripts in the `scripts` directory

* influx_energy_report.py

A script to gather `energy_total` values from InfluxDB and summarise with cost info

Example usage:
`INFLUX_HOST=influx_server.domain.lan INFLUX_DATABASE=database poetry run ./influx_energy_report.py`

## Planned Improvements

* The energy stats gathering could be made generic and support multiple backends, a library will
    be built to share common components here
* We will need more advanced configuration for energy rates and external sources
* A WebUI will be handy for inputting variable data like rates that cannot be pre-seeded
