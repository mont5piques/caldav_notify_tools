#!/usr/bin/env python3
# coding: utf-8

from pytz import reference, utc
from icalendar import Calendar, Event
from datetime import datetime, date, timedelta


def parse_calendar_alarms(calendar_data, event_callback=None, alarm_callback=None):
    # Parsing calendar
    gcal = Calendar.from_ical(calendar_data)
    now = datetime.now()
    today = datetime.date(now)
    utc_now = datetime.utcnow().replace(tzinfo=utc)

    for component in gcal.walk():
        if not component.name == "VEVENT":
            continue

        start = component.get('dtstart').dt
        end = component.get('dtend').dt

        # Look only for ulterior events
        try:
            if isinstance(start, datetime):
                if start < now:
                    continue
            elif isinstance(start, date):
                if start < today:
                    continue
        except TypeError:
            # TZ Datetime comparison error
            if start < utc_now:
                continue

        if not isinstance(start, datetime):
            # It's an all day event,
            start = datetime.combine(start, datetime.min.time())
            start += timedelta(hours=9)

        # If start doesn't contain TZ, add it for uniformity
        if start.tzinfo is None or start.tzinfo.utcoffset(start) is None:
            start = start.replace(tzinfo=reference.LocalTimezone())

        # Trigger event alarm_callback
        if event_callback:
            event_callback(component)

        # Check for alarms
        for subcomp in component.subcomponents:
            if subcomp.name != 'VALARM':
                continue
            if subcomp.get('action') != 'DISPLAY':
                continue

            alarm = subcomp
            trigger = alarm.get('trigger').dt
            alarm_date = start + trigger

            if alarm_callback and alarm_date > utc_now:
                alarm_callback(component, alarm_date)

            # Iterate over all repeats
            if alarm.get('REPEAT'):
                repeats = alarm.get('REPEAT')
                interval = alarm.get('DURATION').dt
                for i in range(repeats):
                    rep_alarm_date = alarm_date + (i+1)*interval

                    if alarm_callback and rep_alarm_date > utc_now:
                        alarm_callback(component, rep_alarm_date)
