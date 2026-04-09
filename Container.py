import pandas as pd, ipaddress
from Generator_IP import random_IP, df_good_valid_ip

#Импортируем список доверенных адресов
good_ip = {ipaddress.ip_address(i) for i in df_good_valid_ip['IP'].values}
raw_ip = random_IP()[0]
def check_ip(raw_ip, good_ip):
    is_valid, is_global, is_trust, final_flag = False, False, False, False
    # Первичная синтаксическая валидация
    try:
        ip = ipaddress.ip_address(raw_ip)
        is_valid = True
    except ValueError:
        is_valid = False
        return(('Получен некорректный IP-адрес. Соединение невозможно'), final_flag)

    # Проврека того, является лм IP-адрес глобальным
    if is_valid == True:
        if ip.is_global == True:
            is_global = True
        else:
            is_global = False
            return(('Соединение невозможно! IP-адрес не является глобальным'), final_flag)

    # Проверка входит ли IP-адресс в список доверенных
    if is_valid == True and is_global == True:
        if ip in good_ip:
            is_trust = True
        else:
            is_trust = False
            return(('Соединение невозможно! IP-адрес не является доверенным'), final_flag)
    if is_valid == True and is_global and is_trust == True:
        final_flag = True
    else:
        final_flag = False
    return(('IP-адресс является валидным, глобальным и доверенным'), final_flag)

print(check_ip(raw_ip, good_ip))

#Поменять эндпоинт и run на ''


