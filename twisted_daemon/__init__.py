import sys
import logging
import requests
from pytz import utc
from datetime import datetime, date, timedelta

from twisted.internet import reactor, task

from calendar_alarms import parse_calendar_alarms
from .log import ColoredFormatter

alarms = []

def refresh_calendar(calendar_url, alarm_callback):
    logging.info("Downloading calendar ...")

    def _alarm_cb(event, alarm_date):
        utc_now = datetime.utcnow().replace(tzinfo=utc)
        diff = alarm_date - utc_now
        seconds = int(diff.total_seconds())

        # Schedule a notification for the alarm
        callID = reactor.callLater(
            seconds,
            lambda: alarm_callback(event)
            )

        logging.info("Running {} in {} secs".format(event.get('summary'), seconds))

        alarms.append(callID)

    try:
        r = requests.get(calendar_url)
        if not r.status_code == 200:
            logging.error("Error while fetching calendar, got HTTP code {}".format(r.status_code))
            return False

        # Cancel all previous alarms
        for alarm in alarms:
            alarm.cancel()

        alarms[:] = []

        # Parse calendar and add all alarms
        parse_calendar_alarms(r.content, alarm_callback=_alarm_cb)
    except Exception as e:
        logging.exception(e)


def run_daemon(calendar_url, alarm_callback):

    # Setting logging
    h1 = logging.StreamHandler(sys.stdout)
    h1.setFormatter(ColoredFormatter("%(levelname)-18s %(message)s"))
    logging.getLogger().addHandler(h1)
    logging.getLogger().setLevel(logging.DEBUG)

    l = task.LoopingCall(refresh_calendar, calendar_url, alarm_callback)
    l.start(40.0)

    reactor.run()
