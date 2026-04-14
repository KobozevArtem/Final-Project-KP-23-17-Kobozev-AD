import pandas as pd, ipaddress, matplotlib.pyplot as plt, os
from Generator_IP import random_IP, df_good_valid_ip
#Секретные ключи 
secret_4 = os.environ["secret_Kobozev_4"]
secret_5 = os.environ["secret_Kobozev_5"]
secret_6 = os.environ["secret_Kobozev_6"]
print(f'Секретный ключ: {secret_4}')

#Импортируем список доверенных адресов
good_ip = {ipaddress.ip_address(i) for i in df_good_valid_ip['IP'].values}
ip, Permission, Reason, type_lst = [], [], [], []
conn_num = list(range(1,11))
#Контейнер проверки IP-адресов
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
#Генерируем 10 случайных IP-адресов и проверяем их
for _ in range(10):
    row = random_IP()
    row_ip = row[0]
    type_IP = row[1]
    ip.append(row_ip)
    Permission.append(check_ip(row_ip, good_ip)[1])
    Reason.append(check_ip(row_ip, good_ip)[0])
    type_lst.append(type_IP)
    
#Контейнер табличного представления результатов проверки
data = {'conn_num': conn_num, 'IP' : ip, 'Permission': Permission,'type': type_lst, 'Reason' : Reason}
df = pd.DataFrame(data)

#Контейнер визуализации результатов проверки
fig, ax = plt.subplots()
k = len(df[df['Permission'] == True])
l = 10 - k
plt.bar(['True', 'False'], [k, l])
ax.set_title('Количество разрешённых и запрещённых соединений')
ax.set_ylabel('Количество')
ax.set_xlabel('Решение')
plt.savefig('bar.png')

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
plt.savefig('pie.png')

print(df)



