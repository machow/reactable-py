from datetime import datetime

from importlib_resources import files
from ..simpleframe import SimpleFrame

us_states = SimpleFrame.read_csv(files("bigblock.data") / "us_states.csv").cast({"Area": int})
cars_93 = SimpleFrame.read_csv(files("bigblock.data") / "cars_93.csv").cast(
    dict(
        mpg_city=int,
        mpg_highway=int,
        price=float,
    )
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
