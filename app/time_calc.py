from datetime import datetime, timedelta, date

def get_date_options():
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%d.%m.%Y")
    today = datetime.now().strftime("%d.%m.%Y")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%d.%m.%Y")
    return [yesterday, today, tomorrow]

def get_cur_time():
    time = datetime.now().strftime('%M')
    return time

def get_user_timezone(user_cur_time_str: str) -> int:
    server_cur_time_str = datetime.now().strftime("%d.%m.%Y %H")
    server_cur_time = datetime.strptime(server_cur_time_str, "%d.%m.%Y %H")
    user_cur_time = datetime.strptime(user_cur_time_str[0:-3], "%d.%m.%Y %H")
    if server_cur_time > user_cur_time:
        hours = server_cur_time - user_cur_time
        return 0 - int(hours.total_seconds() / 3600)
    else:
        hours = user_cur_time - server_cur_time
        return int(hours.total_seconds() / 3600)

def birthday_str_to_dt(birthday_str: str):
    birthday = datetime.strptime(birthday_str, "%d.%m.%Y")
    return birthday

def get_user_death_date(birthday: datetime, years: int):
    birthday_str = birthday.strftime("%d.%m.%Y")
    death_day_str = birthday_str[0:6] + str(int(birthday_str[-4:]) + years)
    death_day = datetime.strptime(death_day_str, "%d.%m.%Y")
    return death_day

def get_user_days_weeks(user_birthday: datetime, user_timezone: int):
    server_cur_time_str = datetime.now().strftime("%d.%m.%Y %H")
    server_cur_time = datetime.strptime(server_cur_time_str, "%d.%m.%Y %H")
    user_cur_time = server_cur_time + timedelta(hours=user_timezone)
    past_days = user_cur_time - user_birthday
    cur_day = past_days + timedelta(days=1)
    past_weeks = past_days.days // 7
    past_days_after_weeks = past_days.days % 7
    return (cur_day.days, past_weeks, past_days_after_weeks)

def get_notification_time_server_tz(notification_time: str, user_tz: int):
    notification_time_user_tz_str = datetime.now().strftime("%d.%m.%Y") + f' {notification_time}'
    notification_time_user_tz = datetime.strptime(notification_time_user_tz_str, "%d.%m.%Y %H:%M")
    notification_time_server_tz = notification_time_user_tz - timedelta(hours=user_tz)
    notification_time_server_tz_str = notification_time_server_tz.strftime("%H:%M")
    return notification_time_server_tz_str

def is_birthday_correct(date_str: str):
    try:
        parsed_date = datetime.strptime(date_str, '%d.%m.%Y').date()
        if (parsed_date < datetime.today().date()) and (parsed_date > date(year=1900, month=1, day=1)):
            return True
    except:
        return False
    
def update_user_tz(old_user_tz: int, new_user_tz: str, old_notifs_time_server_tz: str):
    old_notifs_datetime_server_tz_str = datetime.now().strftime("%d.%m.%Y") + f' {old_notifs_time_server_tz}'
    old_notifs_datetime_server_tz = datetime.strptime(old_notifs_datetime_server_tz_str, "%d.%m.%Y %H:%M")

    new_notifs_datetime_server_tz = old_notifs_datetime_server_tz + timedelta(hours=(old_user_tz - new_user_tz))
    new_notifs_time_server_tz_str = new_notifs_datetime_server_tz.strftime("%H:%M")

    return new_notifs_time_server_tz_str