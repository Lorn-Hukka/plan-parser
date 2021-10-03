from datetime import datetime, timedelta
from json import dumps, loads
import requests, os

FRM = '%Y-%m-%d'

_url = 'https://plany.ath.bielsko.pl/plan.php?type=NaN&cvsfile=true&wd=1&id='

# classes = {
#     '1a': '12633',
#     '1b': '12634',
#     '2a': '12637',
#     '2b': '86036',
#     '3a': '105331',
#     '3b': '105332'
# }

classes = {}

with open("data", 'r', encoding="UTF-8") as f:
    data = loads(f.read())
    for d in data.values():
        classes.update(d)


for c, cid in classes.items():
    print(c, cid)

    new_c = c.replace('/', '_')

    with open(f'plans/plan-{new_c}.ics', 'wb+') as f:
        r = requests.get(_url + str(cid))
        for chunk in r.iter_content(chunk_size=512 * 1024):
            if chunk:
                f.write(chunk)

_plan = {f"w{week:02d}": {} for week in range(53)}


for c in classes.keys():
    _plan = {f"w{week:02d}": {f'd{day}': [] for day in range(7)} for week in range(53)}


    new_c = c.replace('/', '_')

    if not os.path.isfile(f'plans/plan-{new_c}.ics'):
        continue

    with open(f'plans/plan-{new_c}.ics', 'r', encoding="utf-8") as f:
        dataset = f.read().split("BEGIN:VEVENT")

    for data in dataset[1:]:
        _event = data.splitlines()[1:-2:1]

        event = {}
        for prop in _event:
            k, v = prop.split(':')
            event[str(k)] = v

        event.pop("CLASS", None)
        event.pop("SEQUENCE", None)
        event.pop("STATUS", None)
        event.pop("UID", None)
        event.pop("TRANSP", None)
        event.pop("DTSTAMP", None)

        day = datetime.strptime(event.get("DTSTART"), "%Y%m%dT%H%M%SZ").strftime('%w')
        week = datetime.strptime(event.get("DTSTART"), "%Y%m%dT%H%M%SZ").strftime('%W')
        event["DTSTART"] = f'{(datetime.strptime(event.get("DTSTART"), "%Y%m%dT%H%M%SZ") + timedelta(hours = 2))}'
        event["DTEND"] = f'{(datetime.strptime(event.get("DTEND"), "%Y%m%dT%H%M%SZ") + timedelta(hours = 2))}'
        event["LECTURE"], event["TYPE"], event["LECTURER"] = event["SUMMARY"].split()[:3]
        event["ANNOTATION"] = 'NONE'

        _plan[f'w{str(week)}'][f'd{str(day)}'].append(event)

    with open(f'parsed-plans/plan-{new_c}.json', 'wb+') as f:
        f.write(dumps(_plan, indent=4, ensure_ascii=False).encode("utf8"))
