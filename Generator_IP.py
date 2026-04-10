import numpy as np, ipaddress, pandas as pd, random

list_ip = []
#Генерируем глобальные валидные IP-адреса
good_valid_ip = []
np.random.seed(17)
for _ in range(200):
    random_ip = list(np.random.randint(0,256, size=4))
    good_ip = '.'.join([str(i) for i in random_ip])
    if ipaddress.ip_address(good_ip).is_global == True:
        list_ip.append((good_ip, 'Trust_IP'))
        good_valid_ip.append((good_ip, ipaddress.ip_address(good_ip).is_global))

#Эталанные IP-адреса, будем прдполагать, что именно они и есть IP серверов Т-Банка
df_good_valid_ip = pd.DataFrame(good_valid_ip, columns = ['IP', 'Is_global'])

#Генерируем публичные валидные, но чужие IP-адреса
np.random.seed(27)
bad_valid_ip = []
for _ in range(200):
    random_ip = list(np.random.randint(0,256, 4))
    bad_ip = '.'.join([str(i) for i in random_ip])
    good_ip_set = set(df_good_valid_ip['IP'])
    if bad_ip not in good_ip_set:
        list_ip.append((bad_ip, 'Untrust_IP'))
        bad_valid_ip.append((bad_ip, ipaddress.ip_address(bad_ip).is_global))
df2 = pd.DataFrame(bad_valid_ip, columns=['Bad_valid_IP', 'Is_global'])
df_bad_valid_ip = df2[df2['Is_global'] == 1]

#Провереям на то, чтобы IP не совбпадали
dfj = df_good_valid_ip.join(df_bad_valid_ip['Bad_valid_IP'])
dfj['same'] = dfj['IP'] == dfj['Bad_valid_IP']

#Генерируем специальные и привытные IP
private_IP = []
np.random.seed(37)
for _ in range(100):
    bad_1 = list(np.random.randint(0, 256, 3))
    bad_1 = '10.' + '.'.join([str(i) for i in  bad_1])
    private_IP.append((bad_1, ipaddress.ip_address(bad_1).is_private))
    list_ip.append((bad_1, 'Private_IP'))
    bad_2 = list(np.random.randint(0, 256, 2))
    bad_2 = '172.16.' + '.'.join([str(i) for i in bad_2])
    list_ip.append((bad_2, 'Private_IP'))
    private_IP.append((bad_2, ipaddress.ip_address(bad_2).is_private))
    bad_3 = list(np.random.randint(0, 256, 2))
    bad_3 = '192.168.' + '.'.join([str(i) for i in bad_3])
    list_ip.append((bad_3, 'Private_IP'))
    private_IP.append((bad_3, ipaddress.ip_address(bad_3).is_private))
df_private_ip = pd.DataFrame(private_IP, columns=['private_IP','Is_private'])

#Фиксированные паттерны для специальных IP
SPECIAL_NETWORKS = ["10.0.0.0", "192.168.0.0", "127.0.0.0", "169.254.0.0","198.18.0.0","240.0.0.0"]

#Генерируем на основе этих паттернов специальные IP-адреса
np.random.seed(13)
special_ip = []
for _ in range (10):
    for i in SPECIAL_NETWORKS:
        ip = i.split('.')
        ip = '.'.join([j if j != '0' else str(np.random.randint(0,256)) for j in ip])
        special_ip.append((ip, 'Special'))
        list_ip.append((ip, 'Special_IP'))
df_special_IP = pd.DataFrame(special_ip, columns=['IP', 'Is_private'])
#Генерируем "мусорные" IP
np.random.seed(77)
trash_ip = []
for _ in range(50):
    ip = list(np.random.randint(256,999,4))
    trash_ip.append(('.'.join([str(i) for i in ip]), 'Not IP'))
    list_ip.append((('.'.join([str(i) for i in ip])), 'Trash_IP'))
    ip1 = list(np.random.randint(0, 256, 3))
    trash_ip.append(('.'.join([str(i) for i in ip1]), 'Not IP'))
    list_ip.append((('.'.join([str(i) for i in ip1])), 'Trash_IP'))
df_trash_IP = pd.DataFrame(trash_ip, columns=['IP', 'Trash_IP'])
#Теперь мы сгенерировали все необхоимые типы IP-адресов.По итогу емеем список со всеми адресами
#print(list_ip)

#Таблицы с IP-адресами разных типов
#print(df_good_valid_ip)
#print(df_bad_valid_ip)
#print(df_private_ip)
#print(df_trash_IP)

def random_IP():
    return random.choice(list_ip)
