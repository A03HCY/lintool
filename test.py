import lintool.data.network as nk

from rich import print

uuid = nk.find_city_id('jishou').matches[0]

print(uuid)

print(nk.weather_report(uuid.city_id))