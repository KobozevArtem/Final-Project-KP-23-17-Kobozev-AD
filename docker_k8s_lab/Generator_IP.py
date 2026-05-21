import numpy as np
import ipaddress
import pandas as pd
import random

list_ip = []

good_valid_ip = []
np.random.seed(17)

for _ in range(200):
    random_ip = list(np.random.randint(0, 256, size=4))
    good_ip = '.'.join([str(i) for i in random_ip])

    if ipaddress.ip_address(good_ip).is_global:
        list_ip.append((good_ip, 'Trust_IP'))
        good_valid_ip.append((good_ip, ipaddress.ip_address(good_ip).is_global))

df_good_valid_ip = pd.DataFrame(good_valid_ip, columns=['IP', 'Is_global'])

np.random.seed(27)
bad_valid_ip = []

for _ in range(200):
    random_ip = list(np.random.randint(0, 256, 4))
    bad_ip = '.'.join([str(i) for i in random_ip])
    good_ip_set = set(df_good_valid_ip['IP'])

    if bad_ip not in good_ip_set:
        list_ip.append((bad_ip, 'Untrust_IP'))
        bad_valid_ip.append((bad_ip, ipaddress.ip_address(bad_ip).is_global))

df_bad_valid_ip = pd.DataFrame(bad_valid_ip, columns=['Bad_valid_IP', 'Is_global'])
df_bad_valid_ip = df_bad_valid_ip[df_bad_valid_ip['Is_global'] == 1]

private_IP = []
np.random.seed(37)

for _ in range(100):
    bad_1 = list(np.random.randint(0, 256, 3))
    bad_1 = '10.' + '.'.join([str(i) for i in bad_1])
    private_IP.append((bad_1, ipaddress.ip_address(bad_1).is_private))
    list_ip.append((bad_1, 'Private_IP'))

    bad_2 = list(np.random.randint(0, 256, 2))
    bad_2 = '172.16.' + '.'.join([str(i) for i in bad_2])
    private_IP.append((bad_2, ipaddress.ip_address(bad_2).is_private))
    list_ip.append((bad_2, 'Private_IP'))

    bad_3 = list(np.random.randint(0, 256, 2))
    bad_3 = '192.168.' + '.'.join([str(i) for i in bad_3])
    private_IP.append((bad_3, ipaddress.ip_address(bad_3).is_private))
    list_ip.append((bad_3, 'Private_IP'))

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
    for i in SPECIAL_NETWORKS:
        ip = i.split('.')
        ip = '.'.join([j if j != '0' else str(np.random.randint(0, 256)) for j in ip])
        list_ip.append((ip, 'Special_IP'))

np.random.seed(77)

for _ in range(50):
    ip = list(np.random.randint(256, 999, 4))
    list_ip.append(('.'.join([str(i) for i in ip]), 'Trash_IP'))

    ip1 = list(np.random.randint(0, 256, 3))
    list_ip.append(('.'.join([str(i) for i in ip1]), 'Trash_IP'))


def random_IP():
    return random.choice(list_ip)
