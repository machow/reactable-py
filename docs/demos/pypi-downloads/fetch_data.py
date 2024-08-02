# %%
import json
import polars as pl
import requests
from bs4 import BeautifulSoup
from io import StringIO

r = requests.get("https://hugovk.github.io/top-pypi-packages/top-pypi-packages-30-days.min.json")
r.raise_for_status()

monthly = pl.DataFrame(r.json()["rows"]).rename(
    {
        "project": "package",
        "download_count": "downloads_month",
    }
)[:200]


# %%
def fetch_pkg_json(name):
    r = requests.get(f"https://pypi.org/pypi/{name}/json")

    if r.status_code == 404:
        return None

    r.raise_for_status()
    return r.json()


def extract_fields(json):
    fields = [
        "name",
        "author",
        "maintainer",
        "requires_python",
        "requires_dist",
        "home_page",
        "license",
        "package_url",
        "project_urls",
        "summary",
        "version",
    ]

    info = {k: json["info"][k] for k in fields}
    releases = [
        {"release": k, "published_at": fetch_release_time(v)}
        for k, v in reversed(json["releases"].items())
    ][:10]

    return {**info, "releases": releases}


def fetch_release_time(uploads):
    try:
        return uploads[0]["upload_time_iso_8601"]
    except IndexError:
        return None


package_json = list(map(fetch_pkg_json, monthly["package"]))
indx_pypi_missing = [ii for ii, x in enumerate(package_json) if x is None]

simple = list(map(extract_fields, [x for x in package_json if x is not None]))

(
    monthly.with_row_index()
    .filter(~pl.col("index").is_in(indx_pypi_missing))
    .drop("index")
    .write_csv("./pypi-monthly.csv")
)

json.dump(simple, open("./pypi-details.json", "w"))

# %%
