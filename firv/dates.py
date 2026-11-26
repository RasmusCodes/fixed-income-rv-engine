"""Day counts and coupon schedules.

Only what bond and swap analytics need: year fractions for the common conventions and
unadjusted coupon schedules generated backwards from maturity (the market convention for
government bonds; payment-date holiday adjustment does not change accrual).
"""
from __future__ import annotations

import calendar
import datetime as dt

Date = dt.date


def add_months(d: Date, months: int, eom: bool = False) -> Date:
    """Shift by whole months, clamping the day (31 Jan + 1M = 28/29 Feb)."""
    y, m = divmod(d.month - 1 + months, 12)
    year, month = d.year + y, m + 1
    last = calendar.monthrange(year, month)[1]
    day = last if (eom and d.day == calendar.monthrange(d.year, d.month)[1]) else min(d.day, last)
    return dt.date(year, month, day)


def _is_last_of_feb(d: Date) -> bool:
    return d.month == 2 and d.day == calendar.monthrange(d.year, 2)[1]


def year_fraction(start: Date, end: Date, basis: str = "ACT/365F") -> float:
    """Year fraction between two dates.

    basis: ACT/365F, ACT/360, ACT/ACT (ISDA), 30/360 (US bond basis), 30E/360.
    ACT/ACT ICMA needs the coupon period and is handled in :func:`accrual_fraction`.
    """
    b = basis.upper()
    if b in ("ACT/365F", "ACT/365", "A365F"):
        return (end - start).days / 365.0
    if b in ("ACT/360", "A360"):
        return (end - start).days / 360.0
    if b in ("ACT/ACT", "ACT/ACT ISDA"):
        if start == end:
            return 0.0
        sign = 1.0
        if end < start:
            start, end, sign = end, start, -1.0
        total, cur = 0.0, start
        while cur.year < end.year:
            nxt = dt.date(cur.year + 1, 1, 1)
            total += (nxt - cur).days / (366.0 if calendar.isleap(cur.year) else 365.0)
            cur = nxt
        total += (end - cur).days / (366.0 if calendar.isleap(end.year) else 365.0)
        return sign * total
    if b in ("30/360", "30/360 US", "BOND"):
        d1, d2 = start.day, end.day
        if _is_last_of_feb(start) and _is_last_of_feb(end):
            d2 = 30
        if _is_last_of_feb(start):
            d1 = 30
        if d2 == 31 and d1 >= 30:
            d2 = 30
        if d1 == 31:
            d1 = 30
        return (360 * (end.year - start.year) + 30 * (end.month - start.month) + (d2 - d1)) / 360.0
    if b in ("30E/360", "EUROBOND"):
        d1, d2 = min(start.day, 30), min(end.day, 30)
        return (360 * (end.year - start.year) + 30 * (end.month - start.month) + (d2 - d1)) / 360.0
    raise ValueError(f"unknown day count basis {basis!r}")


def coupon_schedule(maturity: Date, frequency: int, start: Date | None = None,
                    eom: bool = True) -> list[Date]:
    """Coupon dates from the first one after ``start`` (exclusive) to maturity, generated
    backwards from maturity. If ``start`` is None, returns dates for the last 100 years."""
    if frequency not in (1, 2, 4, 12):
        raise ValueError("frequency must be 1, 2, 4 or 12")
    step = 12 // frequency
    floor = start or dt.date(maturity.year - 100, maturity.month, 1)
    dates, k = [], 0
    while True:
        d = add_months(maturity, -step * k, eom=eom)
        if d <= floor:
            break
        dates.append(d)
        k += 1
    return dates[::-1]


def previous_coupon(maturity: Date, frequency: int, settle: Date, eom: bool = True) -> Date:
    """Last coupon date on or before ``settle`` (may be before issue for a first period)."""
    step = 12 // frequency
    k = 0
    while True:
        d = add_months(maturity, -step * k, eom=eom)
        if d <= settle:
            return d
        k += 1


def accrual_fraction(prev_cpn: Date, next_cpn: Date, settle: Date, basis: str) -> float:
    """Fraction of the current coupon period that has accrued at ``settle``.

    ACT/ACT ICMA (government bonds): days accrued / days in period.
    30/360 and ACT/360 style bases: year fraction scaled to the period length.
    """
    b = basis.upper()
    if b in ("ACT/ACT ICMA", "ACT/ACT ISMA", "ICMA"):
        return (settle - prev_cpn).days / (next_cpn - prev_cpn).days
    period = year_fraction(prev_cpn, next_cpn, basis)
    return year_fraction(prev_cpn, settle, basis) / period if period > 0 else 0.0
