import jdatetime

from datetime import datetime, date


def jalali_datetime(d, time: bool = True):
    if isinstance(d, date) and not isinstance(d, datetime):
        d = datetime(d.year, d.month, d.day)
    if d is None:
        return "-"
    try:
        if time is True:
            return jdatetime.datetime.fromgregorian(datetime=d).strftime(
                "%Y/%m/%d-%H:%M:%S"
            )
        else:
            return jdatetime.datetime.fromgregorian(datetime=d).strftime("%Y/%m/%d")
    except:
        return "-"


def pretty_jalali_datetime(d):
    if isinstance(d, date) and not isinstance(d, datetime):
        d = datetime(d.year, d.month, d.day)
    if d is None:
        return "-"
    return (
        jdatetime.datetime.fromgregorian(datetime=d)
        .aslocale("fa_IR")
        .strftime("%a, %d %b %Y %H:%M:%S")
    )
