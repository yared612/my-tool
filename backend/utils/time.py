from datetime import datetime,timezone,timedelta

def getCurrentTime():
    dt1 = datetime.utcnow().replace(tzinfo=timezone.utc)
    dt2 = dt1.astimezone(timezone(timedelta(hours=8)))
    currentTime = dt2.strftime("%Y/%m/%d %H:%M:%S")
    return currentTime

def getCurrentMonth():
    dt1 = datetime.utcnow().replace(tzinfo=timezone.utc)
    dt2 = dt1.astimezone(timezone(timedelta(hours=8)))
    currentMonth = dt2.strftime("/%m")
    return currentMonth