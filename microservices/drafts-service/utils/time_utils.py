
from datetime                   import datetime, timezone


def getTime_now() -> str:
    '''
    Returns:
        str: current time as string in isoformat
    '''
    return datetime.now(timezone.utc).isoformat()

def get_diff_in_ms(time1: str, time2: str) -> float:
    '''
    returns the differance between times in milliseconds 
    Args:
        time1 (str): time in isoformat (returend by getTime_now())
        time2 (str): time in isoformat (returend by getTime_now())
    Returns:
        float: the differance between time1 and time2 in milliseconds
    '''
    time1 = datetime.fromisoformat(time1)
    time2 = datetime.fromisoformat(time2)
    return abs((time2 - time1).total_seconds() * 1000)
