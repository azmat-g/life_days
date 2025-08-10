from telebot import formatting
import app.time_calc as tc

from datetime import datetime, timedelta

send_name = formatting.format_text(
    'Добро пожаловать в бот ',
    formatting.hbold('Дни Жизни'),
    '!\n\n',
    'Бот будет ежедневно отправлять вам уведомления о том, который день вы проживаете, а также сколько недель уже прожито.\n\n',
    'Для начала давайте познакомимся. Как вас зовут?',
    separator=''
)

def choose_date_with_name(name: str):
    result = formatting.format_text(
        'Очень приятно, ',
        formatting.hbold(name),
        '! Для корректной работы бота необходимо его настроить.\n\n',
        formatting.hbold('Выберите Вашу текущую дату:'),
        separator=''
    )
    return result

def name_updated(name: str):
    result = formatting.format_text(
        'Имя обновлено, ',
        formatting.hbold(name),
        '!\n\n',
        'Вернуться в профиль - /profile',
        separator=''
    )
    return result

send_correct_name = 'Отправьте имя текстом. Длина имени не должна превышать 30 символов.'

name_skipped = 'Для корректной работы бота необходимо его настроить.\n\nВыберите Вашу текущую дату:'

choose_date = formatting.format_text(
    'Добро пожаловать в бот ',
    formatting.hbold('Дни Жизни'),
    '!\n\nПеред началом работы необходимо настроить бота.\n\nВыберите Вашу текущую дату:',
    separator=''
)

choose_time = 'Отлично, теперь выберите ваше текущее время:'

def is_datetime_correct(datetime: str):
    result = formatting.format_text(
        'Текущие дата и время: ',
        formatting.hbold(datetime),
        '?',
        separator='')
    return result

send_birthday = formatting.format_text(
    'Теперь отправьте дату Вашего рождения в формате "',
    formatting.hbold('ДД.ММ.ГГГГ'),
    '", например ',
    formatting.hcode('07.05.2000'),
    separator=''
)

def date_is_incorrect(date_str: str):
    result = formatting.format_text(
        'Некорректно указана дата. Попробуйте отправить еще раз.\n\n',
        'Дата рождения должна:\n',
        '- соответствовать формату "',
        formatting.hbold('ДД.ММ.ГГГГ'),
        '";\n',
        '- быть раньше сегодняшнего дня;\n',
        '- быть позже 1900-го года.\n\n',
        'Например, ',
        formatting.hcode('07.05.2000'),
        ' (нажмите на дату, чтобы скопировать).\n\n',
        'Вы указали: ',
        formatting.hbold(date_str),
        separator=''
    )
    return result

send_date_in_text = formatting.format_text(
    'Отправьте дату текстом в формате "',
    formatting.hbold('ДД.ММ.ГГГГ'),
    '".\n\nНапример, ',
    formatting.hcode('07.05.2000'),
    ' (нажмите на дату, чтобы скопировать).',
    separator=''
)

def days_weeks_left_reg(cur_day: int, past_weeks: int, past_days_after_weeks: int):
    past_weeks_postfix = ''
    past_days_after_weeks_postfix = ''
    cur_day_str = str(cur_day)
    past_weeks_str = str(past_weeks)
    if len(cur_day_str) > 3:
        cur_day_str = (cur_day_str[0:-3] + ' ' + cur_day_str[-3:])
    if len(past_weeks_str) > 3:
        past_weeks_str = (past_weeks_str[0:-3] + ' ' + past_weeks_str[-3:])

    if past_weeks in (11, 12, 13, 14):
        past_weeks_postfix = ' недель'
    elif past_weeks % 10 == 1:
        past_weeks_postfix = ' неделю'
    elif past_weeks % 10 in (2, 3, 4):
        past_weeks_postfix = ' недели'
    else:
        past_weeks_postfix = ' недель'
    if past_days_after_weeks % 10 == 1:
        past_days_after_weeks_postfix = ' день'
    elif past_days_after_weeks % 10 in (2, 3, 4):
        past_days_after_weeks_postfix = ' дня'
    else:
        past_days_after_weeks_postfix = ' дней'
    result = formatting.format_text(
        'Сейчас Вы проживаете свой ',
        formatting.hbold(cur_day_str +'-й день'),
        '. Прожито ',
        formatting.hbold(past_weeks_str + past_weeks_postfix),
        (' и ' + formatting.hbold(str(past_days_after_weeks) + past_days_after_weeks_postfix))
        if past_days_after_weeks else formatting.format_text(
            ', началась ',
            formatting.hbold(str(past_weeks + 1) + '-я'),
            separator=''
        ),
        '.',
        separator=''
    )
    return result

choose_notifications_hours = 'Выберите час для отправки ежедневных уведомлений (минуты можно будет указать на следующем шаге):'

choose_notifications_mins = 'Выберите время для отправки ежедневных уведомлений:'

def notification_time_set(notification_time: str):
    result = formatting.format_text(
        'Уведомления будут приходить ежедневно в ',
        formatting.hbold(notification_time),
        '.\n\n',
        'Чтобы посмотреть свой профиль и настройки, нажмите /profile',
        separator=''
    )
    return result

def everyday_notification(cur_day: int, past_weeks: int, past_days_after_weeks: int, name: str | None):
    cur_day_str, past_weeks_str = str(cur_day), str(past_weeks)
    past_weeks_prefix = ''
    past_weeks_postfix = ''
    past_days_after_weeks_postfix = ''
    cur_week_str = str(past_weeks + 1)
    if len(cur_day_str) > 3:
        cur_day_str = (cur_day_str[0:-3] + ' ' + cur_day_str[-3:])
    if len(past_weeks_str) > 3:
        past_weeks_str = (past_weeks_str[0:-3] + ' ' + past_weeks_str[-3:])
    if len(cur_week_str) > 3:
        cur_week_str = (cur_week_str[0:-3] + ' ' + cur_week_str[-3:])
    if past_weeks in (11, 12, 13, 14):
        past_weeks_prefix = 'Прожито '
        past_weeks_postfix = ' недель'
    elif past_weeks % 10 == 1:
        past_weeks_prefix = 'Прожита '
        past_weeks_postfix = ' неделя'
    elif past_weeks % 10 in (2, 3, 4):
        past_weeks_prefix = 'Прожито '
        past_weeks_postfix = ' недели'
    else:
        past_weeks_prefix = 'Прожито '
        past_weeks_postfix = ' недель'
    if past_days_after_weeks % 10 == 1:
        past_days_after_weeks_postfix = ' день'
    elif past_days_after_weeks % 10 in (2, 3, 4):
        past_days_after_weeks_postfix = ' дня'
    else:
        past_days_after_weeks_postfix = ' дней'
    
    result = formatting.format_text(
        f'Здравствуйте, {name}! ' if name else
        'Здравствуйте! ',
        'Вы проживаете свой ',
        formatting.hbold(cur_day_str + '-й день'),
        '. ',
        past_weeks_prefix,
        formatting.hbold(past_weeks_str + past_weeks_postfix),
        (' и ' + formatting.hbold(str(past_days_after_weeks) + past_days_after_weeks_postfix))
        if past_days_after_weeks else
        (', началась ' + formatting.hbold('неделя ' + cur_week_str + ', день 1-й')),
        '.',
        separator=''
    )
    return result

timezone_updated = 'Часовой пояс обновлен!\n\nПерейти в профиль - /profile'

def birthday_updated(birthday: str):
    result = formatting.format_text(
        'Дата рождения изменена на ',
        formatting.hbold(birthday),
        '!',
        '\n\nПерейти в профиль - /profile',
        separator=''
    )
    return result

def notifs_time_updated(notification_time: str):
    result = formatting.format_text(
        'Уведомления будут приходить ежедневно в ',
        formatting.hbold(notification_time),
        '.',
        '\n\nПерейти в профиль - /profile',
        separator=''
    )
    return result

def get_profile_info(user_info_dict: dict):
    is_subscription_active = user_info_dict['is_subscription_active']
    result = None
    if is_subscription_active:
        if user_info_dict['user_birthday_dt'] and user_info_dict['is_user_timezone']:
            cur_day, past_weeks, past_days_after_weeks = tc.get_user_days_weeks(
                user_birthday=user_info_dict['user_birthday_dt'],
                user_timezone=user_info_dict['user_timezone_int']
            )
            cur_day_str, past_weeks_str = str(cur_day), str(past_weeks)
            past_weeks_postfix = ''
            past_days_after_weeks_postfix = ''
            if len(cur_day_str) > 3:
                cur_day_str = (cur_day_str[0:-3] + ' ' + cur_day_str[-3:])
            if len(past_weeks_str) > 3:
                past_weeks_str = (past_weeks_str[0:-3] + ' ' + past_weeks_str[-3:])
            if past_weeks in (11, 12, 13, 14):
                past_weeks_postfix = ' недель'
            elif past_weeks % 10 == 1:
                past_weeks_postfix = ' неделю'
            elif past_weeks % 10 in (2, 3, 4):
                past_weeks_postfix = ' недели'
            else:
                past_weeks_postfix = ' недель'
            if past_days_after_weeks % 10 == 1:
                past_days_after_weeks_postfix = ' день'
            elif past_days_after_weeks % 10 in (2, 3, 4):
                past_days_after_weeks_postfix = ' дня'
            else:
                past_days_after_weeks_postfix = ' дней'

        result = formatting.format_text(
            ('Сейчас Вы проживаете свой ' +
            formatting.hbold(cur_day_str + '-й день')+
            '. Прожито '+
            formatting.hbold(past_weeks_str + past_weeks_postfix)+
            (' и ' + formatting.hbold(str(past_days_after_weeks) + past_days_after_weeks_postfix))
            if past_days_after_weeks else formatting.format_text(
                ', началась ',
                formatting.hbold(str(past_weeks + 1) + '-я'),
                separator=''
            )) if (user_info_dict['user_birthday_dt'] and user_info_dict['is_user_timezone']) else
            ('Указаны не все данные, необходимые для работы бота'),
            '.\n\n',
            'Ваш профиль:\n\n',
            'Имя - ',
            formatting.hbold(
                user_info_dict['user_name'] if
                user_info_dict['user_name'] else
                'Не указано'
            ),
            '\nТекущее время - ',
            formatting.hbold(user_info_dict['cur_user_time_str']) if user_info_dict['cur_user_time_str'] else
            formatting.hbold('Не указан часовой пояс'),
            '\nДата рождения - ',
            formatting.hbold(user_info_dict['birthday_str']) if user_info_dict['birthday_str'] else
            formatting.hbold('Не указана'),
            '\nВремя уведомлений - ',
            formatting.hbold(user_info_dict['notifs_time_str']) if user_info_dict['notifs_time_str'] else
            formatting.hbold('Не указано'),
            '\nПодписка активна до - ',
            formatting.hbold(user_info_dict['subscription_end_str']),
            '\n\nВыберите, что хотите изменить ⬇️',
            separator=''
        )
    else:
        result = formatting.format_text(
            'Ваша подписка истекла.',
            '\n\n',
            'Ваш профиль:\n\n',
            'Имя - ',
            formatting.hbold(
                user_info_dict['user_name'] if
                user_info_dict['user_name'] else
                'Не указано'
            ),
            '\nТекущее время - ',
            formatting.hbold(user_info_dict['cur_user_time_str']) if user_info_dict['cur_user_time_str'] else
            formatting.hbold('Не указан часовой пояс'),
            '\nДата рождения - ',
            formatting.hbold(user_info_dict['birthday_str']) if user_info_dict['birthday_str'] else
            formatting.hbold('Не указана'),
            '\nВремя уведомлений - ',
            formatting.hbold(user_info_dict['notifs_time_str']) if user_info_dict['notifs_time_str'] else
            formatting.hbold('Не указано'),
            '\nПодписка активна до - ',
            formatting.hbold(user_info_dict['subscription_end_str']),
            '\n\nВыберите, что хотите изменить ⬇️',
            separator=''
        )
    return result

def get_subscr_end(subscr_end: str):
    result = formatting.format_text(
        'Подписка активна до ',
        formatting.hbold(subscr_end),
        '\n\nНа данный момент продлевать подписку можно только разовыми платежами.',
        # '\n\nМожно продлевать подписку единовременными платежами, ',
        # 'а можно оформить постоянную подписку с автоматическими ежемесячными списаниями.',
        separator=''
    )
    return result

def subscription_expires(end_date: datetime, user_tz: int):
    end_date_user_tz = (end_date + timedelta(hours=user_tz)).strftime('%d.%m.%Y %H:%M')
    result = formatting.format_text(
        'Ваша подписка скоро закончится. Активна до ',
        formatting.hbold(end_date_user_tz),
        '.',
        separator=''
    )
    return result

about_subscription = formatting.format_text(
    'Если подписка истекает ',
    formatting.hbold('в будущем'),
    ', то она будет продлена исходя из срока окончания текущей подписки.\n\n',
    'Например, сегодня ',
    formatting.hbold('1-е мая'),
    ', текущая подписка активна до ',
    formatting.hbold('3-го мая'),
    '. Вы оплатили продление подписки на ',
    formatting.hbold('30 дней'),
    ' - она будет продлена до ',
    formatting.hbold('2-го июня'),
    ' (', formatting.hbold('3-е мая + 30 дней'), ').\n\n',
    'Если подписка ',
    formatting.hbold('уже истекла'),
    ' и вы хотите ее продлить, то она будет продлена исходя из момента оплаты.\n\n',
    'Например, подписка закончилась ',
    formatting.hbold('25-го апреля'),
    ', а сегодня ', formatting.hbold('1-е мая'),
    ' и вы хотите продлить ее на ',
    formatting.hbold('30 дней'),
    ' - то подписка будет продлена до ',
    formatting.hbold('31-го мая'),
    ' (', formatting.hbold('1-е мая + 30 дней'), ').',
    separator=''
)

disable_bot = 'Вы действительно хотите отключить бота? Оставшиеся дни подписки сгорят.'

bot_is_disabled = 'Бот отключен и больше не будет присылать Вам уведомления.\n\nДля активации бота нажмите /start'

bot_stays_active = 'Бот будет продолжать присылать Вам уведомления.'

bot_is_active_full_user = 'Бот активен. Чтобы узнать информацию о профиле и подписке нажмите /profile'

bot_is_active__not_full_user = 'Бот активен. Для корректной работы бота необходимо указать Ваши данные в профиле.\n\n' \
                                'Чтобы это сделать нажмите /profile'

timezone_is_unknown = formatting.format_text(
    'Для начала нужно указать часовой пояс.\n\n',
    formatting.hbold('Выберите Вашу текущую дату:'),
    separator=''
)

def prolong_subscription(days: str, cost: str):
    result = formatting.format_text(
        'Продление подписки на ',
        days,
        ' дней, ',
        cost,
        ' RUB\n\n',
        formatting.hbold('❗После оплаты нажмите "Проверить оплату 🔎"❗'),
         separator=''
    )
    return result