from datetime import datetime

def parse_date(date_str):
    date = datetime.strptime(date_str, "%d-%m-%y")
    return date.year, date.timetuple().tm_yday, date.date() 