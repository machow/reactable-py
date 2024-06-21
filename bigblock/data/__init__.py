from importlib_resources import files
from ..simpleframe import SimpleFrame

us_states = SimpleFrame.read_csv(files("bigblock.data") / "us_states.csv")
