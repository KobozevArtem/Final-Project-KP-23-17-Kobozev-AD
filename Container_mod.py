import ipaddress, random, pandas as pd, matplotlib.pyplot as plt, os
from Generator_IP import random_IP, df_good_valid_ip

#Список URL-адресов для тестов 
url_list = ['https://www.tbank.ru', 'http://www.tbank.ru', 'www.tbank.ru', 'https://www.tbank.ru', 'https://www.tbank.ru', 'https:\\www.tbank.ru']
#Функция для выбора случайного URL-адреса
def random_url():
        return random.choice(url_list)

# Доверенные IP-адреса серверов банка
good_ip = {ipaddress.ip_address(ip) for ip in df_good_valid_ip["IP"].values}
#Проверка IP-адреса
def check_ip(raw_ip, trusted_ips):
    final_flag = False
    try:
        ip = ipaddress.ip_address(raw_ip)
    except ValueError:
        return "Получен некорректный IP-адрес. Соединение невозможно", final_flag

    if not ip.is_global:
        return "Соединение невозможно! IP-адрес не является глобальным", final_flag

    if ip not in trusted_ips:
        return "Соединение невозможно! IP-адрес не является доверенным", final_flag

    final_flag = True
    return "IP-адрес является валидным, глобальным и доверенным", final_flag
#Проверка URL-адреса
def check_https(url):
    if not isinstance(url, str) or not url:
        return "Некорректный URL. Соединение невозможно", False
    if url.startswith("https://"):
        return "Используется защищённый протокол HTTPS", True
    if url.startswith("http://"):
        return "Соединение невозможно! Используется небезопасный протокол HTTP", False
    return "Некорректная схема URL. Требуется HTTPS", False
def final_check(url, raw_ip, trusted_ips):
    ip_message, ip_permission = check_ip(raw_ip, trusted_ips)
    if not ip_permission:
        return ip_message, False
    url_message, url_permission = check_https(url)
    if not url_permission:
        return url_message, False
    return "Соединение разрешено: IP доверенный, используется безопасный HTTPS", True

urls, ip, Permission, Reason, type_lst = [], [], [], [], []
conn_num = list(range(1,11))
for _ in range(10):
    row = random_IP()
    row_ip = row[0]
    type_IP = row[1]
    url = random_url()
    result_message, result_permission = final_check(url, row_ip, good_ip)
    urls.append(url)
    ip.append(row_ip)
    Permission.append(result_permission)
    Reason.append(result_message)
    type_lst.append(type_IP)

#Контейнер табличного представления результатов проверки
data = {'conn_num': conn_num, 'IP' : ip, 'URLS': urls, 'Permission': Permission,'type': type_lst, 'Reason' : Reason}
df = pd.DataFrame(data)
print(df)

fig, ax = plt.subplots()
k = len(df[df['Permission'] == True])
l = 10 - k
plt.bar(['True', 'False'], [k, l])
ax.set_title('Количество разрешённых и запрещённых соединений')
ax.set_ylabel('Количество')
ax.set_xlabel('Решение')
plt.savefig('barm.png')

fig, ax = plt.subplots()
a = len(df[df['type'] == 'Trust_IP'])
b = len(df[df['type'] == 'Untrust_IP'])
c = len(df[df['type'] == 'Private_IP'])
d = len(df[df['type'] == 'Special_IP'])
f = len(df[df['type'] == 'Trash_IP'])

sizes = [a, b, c, d, f]
labels = ['Trust_IP', 'Untrust_IP', 'Private_IP', 'Special_IP', 'Trash_IP']
ax.pie(sizes,labels=labels,autopct='%1.1f%%',startangle=90,labeldistance=1.1,  pctdistance=0.7,wedgeprops={'edgecolor': 'black', 'linewidth': 1})
ax.set_title('Типы IP-адресов')
plt.savefig('piem.png')

