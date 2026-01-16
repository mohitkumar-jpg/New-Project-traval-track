# core/utils/timezones.py
import pytz
from datetime import datetime

def get_gmt_timezones():
    zones = []
    now = datetime.utcnow()

    for tz_name in pytz.common_timezones:
        tz = pytz.timezone(tz_name)
        offset = tz.utcoffset(now)

        if offset is None:
            continue

        total_minutes = int(offset.total_seconds() / 60)
        hours, minutes = divmod(abs(total_minutes), 60)
        sign = "+" if total_minutes >= 0 else "-"

        gmt = f"GMT{sign}{hours:02d}:{minutes:02d}"

        # Pretty name
        label = f"({gmt}) {tz_name.replace('_', ' ')}"

        zones.append((tz_name, label))

    return sorted(zones, key=lambda x: x[1])
