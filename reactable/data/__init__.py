import json

from datetime import datetime

from importlib_resources import files
from ..simpleframe import SimpleFrame

BIG_DATA = files("reactable.data")

__all__ = [
    "cars_93",
    "co2",
    "nottem",
    "penguins",
    "prices",
    "sleep",
    "starwars",
    "us_states",
    "us_expenditures",
]

cars_93 = SimpleFrame.read_csv(BIG_DATA / "cars_93.csv").cast(
    dict(
        mpg_city=int,
        mpg_highway=int,
        price=float,
        min_price=float,
        max_price=float,
    )
)

co2 = SimpleFrame.read_csv(BIG_DATA / "co2.csv").cast(
    dict(
        conc=int,
        uptake=float,
    )
)

nottem = SimpleFrame.read_csv(BIG_DATA / "nottem.csv").cast(
    dict(
        year=int,
        Jan=float,
        Feb=float,
        Mar=float,
        Apr=float,
        May=float,
        Jun=float,
        Jul=float,
        Aug=float,
        Sep=float,
        Oct=float,
        Nov=float,
        Dec=float,
    )
)

penguins = SimpleFrame.read_csv(BIG_DATA / "penguins.csv").cast(
    dict(
        bill_length_mm=float,
        bill_depth_mm=float,
        flipper_length_mm=float,
        body_mass_g=float,
        year=int,
        sex=str
    ),
    na_char="NA"
)

prices = SimpleFrame.from_dict(
    {
        "price_usd": [123456.56, 132, 5650.12],
        "price_inr": [350, 23208.552, 1773156.4],
        "number_fr": [123456.56, 132, 5650.12],
        "temp": [22, None, 31],
        "percent": [0.9525556, 0.5, 0.112],
        "date": [datetime(2019, 1, 2), datetime(2019, 3, 15), datetime(2019, 9, 22)],
    }
)

sleep = SimpleFrame.read_csv(BIG_DATA / "sleep.csv").cast(
    dict(
        extra=float,
        group=int,
        id=int,
    )
)

starwars = SimpleFrame.from_dict(json.load((BIG_DATA / "starwars.json").open()))

us_states = SimpleFrame.read_csv(BIG_DATA / "us_states.csv").cast({"Area": int})
us_expenditures = SimpleFrame.read_csv(BIG_DATA / "us_expenditures.csv")
