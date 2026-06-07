# ==============================
# БЛОК 1. ПОДКЛЮЧЕНИЕ БИБЛИОТЕК
# ==============================

import numpy as np
import ipaddress
import pandas as pd
import random


# ==============================
# БЛОК 2. ИНИЦИАЛИЗАЦИЯ СПИСКОВ ДАННЫХ
# ==============================

# Общий список IP-адресов.
# В него добавляются адреса разных типов:
# Trust_IP, Untrust_IP, Private_IP, Special_IP, Trash_IP.
list_ip = []

# Список доверенных валидных глобальных IP-адресов.
good_valid_ip = []


# ==============================
# БЛОК 3. ГЕНЕРАЦИЯ ДОВЕРЕННЫХ ГЛОБАЛЬНЫХ IP
# ==============================

# Фиксируем seed, чтобы при каждом запуске получался одинаковый набор адресов.
np.random.seed(17)

for _ in range(200):
    # Генерируем 4 числа от 0 до 255 для формирования IPv4-адреса.
    random_ip = list(np.random.randint(0, 256, size=4))

    # Преобразуем список чисел в строку формата "x.x.x.x".
    good_ip = ".".join([str(i) for i in random_ip])

    # Проверяем, является ли IP глобальным.
    # Только глобальные IP попадают в доверенный список.
    if ipaddress.ip_address(good_ip).is_global:
        list_ip.append((good_ip, "Trust_IP"))

        # Сохраняем IP и признак глобальности для дальнейшего формирования DataFrame.
        good_valid_ip.append((good_ip, ipaddress.ip_address(good_ip).is_global))


# Формируем таблицу доверенных глобальных IP.
# Она используется в main.py для создания множества good_ip.
df_good_valid_ip = pd.DataFrame(
    good_valid_ip,
    columns=["IP", "Is_global"]
)


# ==============================
# БЛОК 4. ГЕНЕРАЦИЯ НЕДОВЕРЕННЫХ ГЛОБАЛЬНЫХ IP
# ==============================

np.random.seed(27)

bad_valid_ip = []

for _ in range(200):
    # Генерируем случайный IPv4-адрес.
    random_ip = list(np.random.randint(0, 256, 4))
    bad_ip = ".".join([str(i) for i in random_ip])

    # Получаем множество доверенных IP, чтобы не добавить их повторно как недоверенные.
    good_ip_set = set(df_good_valid_ip["IP"])

    # Если IP не входит в доверенный список, считаем его недоверенным.
    if bad_ip not in good_ip_set:
        list_ip.append((bad_ip, "Untrust_IP"))

        # Сохраняем IP и признак глобальности.
        bad_valid_ip.append((bad_ip, ipaddress.ip_address(bad_ip).is_global))


# Формируем таблицу недоверенных IP.
df_bad_valid_ip = pd.DataFrame(
    bad_valid_ip,
    columns=["Bad_valid_IP", "Is_global"]
)

# Оставляем только глобальные недоверенные IP.
df_bad_valid_ip = df_bad_valid_ip[df_bad_valid_ip["Is_global"] == 1]


# ==============================
# БЛОК 5. ГЕНЕРАЦИЯ ЧАСТНЫХ IP-АДРЕСОВ
# ==============================

private_IP = []

np.random.seed(37)

for _ in range(100):
    # Генерация адресов диапазона 10.0.0.0/8.
    bad_1 = list(np.random.randint(0, 256, 3))
    bad_1 = "10." + ".".join([str(i) for i in bad_1])

    # Проверяем, что адрес действительно является частным.
    private_IP.append((bad_1, ipaddress.ip_address(bad_1).is_private))
    list_ip.append((bad_1, "Private_IP"))

    # Генерация адресов диапазона 172.16.0.0/12.
    bad_2 = list(np.random.randint(0, 256, 2))
    bad_2 = "172.16." + ".".join([str(i) for i in bad_2])

    private_IP.append((bad_2, ipaddress.ip_address(bad_2).is_private))
    list_ip.append((bad_2, "Private_IP"))

    # Генерация адресов диапазона 192.168.0.0/16.
    bad_3 = list(np.random.randint(0, 256, 2))
    bad_3 = "192.168." + ".".join([str(i) for i in bad_3])

    private_IP.append((bad_3, ipaddress.ip_address(bad_3).is_private))
    list_ip.append((bad_3, "Private_IP"))


# ==============================
# БЛОК 6. ГЕНЕРАЦИЯ СПЕЦИАЛЬНЫХ И СЛУЖЕБНЫХ IP
# ==============================

# Список сетей, которые используются как основа для служебных адресов.
SPECIAL_NETWORKS = [
    "10.0.0.0",
    "192.168.0.0",
    "127.0.0.0",
    "169.254.0.0",
    "198.18.0.0",
    "240.0.0.0"
]

np.random.seed(13)

for _ in range(10):
    for network in SPECIAL_NETWORKS:
        # Разбиваем адрес на октеты.
        ip = network.split(".")

        # Заменяем нулевые октеты случайными значениями.
        # Так формируются разные варианты специальных IP.
        ip = ".".join([
            part if part != "0" else str(np.random.randint(0, 256))
            for part in ip
        ])

        # Добавляем адрес в общий список как специальный.
        list_ip.append((ip, "Special_IP"))


# ==============================
# БЛОК 7. ГЕНЕРАЦИЯ НЕКОРРЕКТНЫХ IP
# ==============================

np.random.seed(77)

for _ in range(50):
    # Генерируем адрес с числами больше 255.
    # Такой IP является синтаксически некорректным.
    ip = list(np.random.randint(256, 999, 4))
    list_ip.append((".".join([str(i) for i in ip]), "Trash_IP"))

    # Генерируем адрес из трёх октетов вместо четырёх.
    # Такой IP тоже является некорректным.
    ip1 = list(np.random.randint(0, 256, 3))
    list_ip.append((".".join([str(i) for i in ip1]), "Trash_IP"))


# ==============================
# БЛОК 8. ВЫДАЧА СЛУЧАЙНОГО IP ДЛЯ ПРОВЕРКИ
# ==============================

def random_IP():
    """
    Функция возвращает случайный IP-адрес из общего списка.
    Используется в main.py для формирования таблицы проверяемых соединений.
    """

    return random.choice(list_ip)
