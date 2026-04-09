import pandas as pd, numpy as np, matplotlib.pyplot as plt
from sympy import *

# Общая часть пункт 1
"""print('Общая часть пункт 1')
k, c, t, l = symbols('k c t l')
c_ost = 100000
am_lst = []
c_ost_lst = []
for i in range(5):
  Am = (c - l)/t
  c_ost -= Am.subs({c:100000, l:0, t:5})
  am_lst.append(round(Am.subs({c:100000, l:0, t:5}), 2))
  c_ost_lst.append(round(c_ost, 2))
print('Am_list', am_lst)
print('c_ost_list', c_ost_lst)

#Общая часть пункт 2
print('Общая часть пункт 2')
Aj = 0
C_ost = 100000
am_lst2 = []
c_ost_lst2 = []
for i in range(5):
  Am = k * 1/t * (c - Aj)
  C_ost -= Am.subs({k:2, t:5, c:100000})
  c_ost_lst2.append(round(C_ost, 2))
  Aj += Am
  am_lst2.append(round(Am.subs({k:2, t:5, c:100000}), 2))
print('Am_lst2:', am_lst2)
print('c_ost_lst2:', c_ost_lst2)

#Общая часть пункт 3
print('Общая часть пункт 3')
k1, c1, t1, l1 = symbols('k1 c1 t1 l1')
c_ost1 = 30000
am_lst3 = []
c_ost_lst3 = []
for i in range(8):
  Am = (c1 - l1)/t1
  c_ost1 -= Am.subs({c1:30000, l1:0, t1:8})
  am_lst3.append(round(Am.subs({c1:30000, l1:0, t1:8}), 2))
  c_ost_lst3.append(round(c_ost1, 2))
print('Am_list3', am_lst3)
print('c_ost_list3', c_ost_lst3)                 

Aj1 = 0
C_ost1 = 30000
am_lst4 = []
c_ost_lst4 = []
for i in range(8):
  Am = k1 * 1/t1 * (c1 - Aj1)
  C_ost1 -= Am.subs({k1:2, t1:8, c1:30000})
  c_ost_lst4.append(round(C_ost1, 2))
  Aj1 += Am
  am_lst4.append(round(Am.subs({k1:2, t1:8, c1:30000}), 2))
print('Am_lst4:', am_lst4)
print('c_ost_lst4:', c_ost_lst4)
#Создание таблиц
print('')
Y = range(1, 9)
table1 = zip(Y, am_lst3, c_ost_lst3)
table2 = zip(Y, am_lst4, c_ost_lst4)
tframe = pd.DataFrame(table1, columns = ['Y', 'am_lst3', 'c_ost_lst3'])
tframe2 = pd.DataFrame(table2, columns = ['Y', 'am_lst4', 'c_ost_lst4'])
print(tframe)
print(tframe2)

#Визуализация
plt.figure()
plt.plot(tframe['Y'], tframe['c_ost_lst3'], label = 'Линейная аммортизация')
plt.ylabel('Остаточная стоимость')
plt.xlabel('Год')
plt.savefig('picture1.png')

plt.figure()
plt.plot(tframe2['Y'], tframe2['c_ost_lst4'], label = 'Ускоренная аммортизация')
plt.ylabel('Остаточнаяz стоимость')
plt.xlabel('Год')
plt.savefig('picture2.png')

vals = am_lst3
labels = [str(x) for x in range(1,9)]
explode = [0.1] * 8
fig, ax = plt.subplots()
plt.pie(vals, labels = labels, explode=explode, autopct = '%1.1f%%', shadow = True, wedgeprops={'lw':1, 'ls':'-', 'edgecolor':'k'}, 
rotatelabels = False)
ax.axis('equal')
plt.savefig('picture3.png')

vals2 = am_lst4
labels2 = [str(x) for x in range(1,9)]
fig, ax = plt.subplots()
plt.pie(vals2, labels = labels, explode=explode, autopct = '%1.1f%%', shadow = True, wedgeprops={'lw':1, 'ls':'-', 'edgecolor':'k'}, 
rotatelabels = False)
plt.savefig('picture4.png')

fig, ax = plt.subplots()
plt.bar(tframe['Y'], tframe['am_lst3'])
plt.savefig('picture5.png')

fig, ax = plt.subplots()
plt.bar(tframe2['Y'], tframe2['am_lst4'])
plt.savefig('picture6.png')
print('')

#Индвидулаьная часть задания
print('Индвидулаьная часть задания')
k2, c2, t2, l2 = symbols('k2 c2 t2 l2')
c_ost2 = 90000
am_lst5 = []
c_ost_lst5 = []
for i in range(9):
  Am = (c2 - l2)/t2
  c_ost2 -= Am.subs({c2:90000, l2:0, t2:9})
  am_lst5.append(round(Am.subs({c2:90000, l2:0, t2:9}), 2))
  c_ost_lst5.append(round(c_ost2, 2))
print('Am_list5', am_lst5)
print('c_ost_list5', c_ost_lst5)                 

Aj2 = 0
C_ost2 = 90000
am_lst6 = []
c_ost_lst6 = []
for i in range(9):
  Am = k2 * 1/t2 * (c2 - Aj2)
  C_ost2 -= Am.subs({k2:2, t2:9, c2:90000})
  c_ost_lst6.append(round(C_ost2, 2))
  Aj2 += Am
  am_lst6.append(round(Am.subs({k2:2, t2:9, c2:90000}), 2))
print('Am_lst6:', am_lst6)
print('c_ost_lst6:', c_ost_lst6)
#Создание таблиц
print('')
Y = range(1, 10)
table3 = zip(Y, am_lst5, c_ost_lst5)
table4 = zip(Y, am_lst6, c_ost_lst6)
tframe3 = pd.DataFrame(table3, columns = ['Y', 'am_lst5', 'c_ost_lst5'])
tframe4 = pd.DataFrame(table4, columns = ['Y', 'am_lst6', 'c_ost_lst6'])
print(tframe3)
print(tframe4)

#Визуализация
plt.figure()
plt.plot(tframe3['Y'], tframe3['c_ost_lst5'], label = 'Линейная аммортизация')
plt.ylabel('Остаточная стоимость')
plt.xlabel('Год')
plt.savefig('picture7.png')

plt.figure()
plt.plot(tframe4['Y'], tframe4['c_ost_lst6'], label = 'Ускоренная аммортизация')
plt.ylabel('Остаточнаяz стоимость')
plt.xlabel('Год')
plt.savefig('picture8.png')

vals3 = am_lst5
labels = [str(x) for x in range(1,10)]
explode = [0.1] * 9
fig, ax = plt.subplots()
plt.pie(vals3, labels = labels, explode=explode, autopct = '%1.1f%%', shadow = True, wedgeprops={'lw':1, 'ls':'-', 'edgecolor':'k'}, 
rotatelabels = False)
ax.axis('equal')
plt.savefig('picture9.png')

vals4 = am_lst6
labels2 = [str(x) for x in range(1,10)]
fig, ax = plt.subplots()
plt.pie(vals4, labels = labels, explode=explode, autopct = '%1.1f%%', shadow = True, wedgeprops={'lw':1, 'ls':'-', 'edgecolor':'k'}, 
rotatelabels = False)
plt.savefig('picture10.png')

fig, ax = plt.subplots()
plt.bar(tframe3['Y'], tframe3['am_lst5'])
plt.savefig('picture11.png')

fig, ax = plt.subplots()
plt.bar(tframe4['Y'], tframe4['am_lst6'])
plt.savefig('picture12.png')"""

# Задание 1 Кобозев Батулин
import os

secret_1 = os.environ["secret_Kobozev_1"]
secret_2 = os.environ["secret_Kobozev_2"]
secret_3 = os.environ["secret_Kobozev_3"]
print(secret_2)

#С графиками все в порядке, 5 (Оценил Якушенко И.С.)

# Задание 2 Кобозев Якушенко
k2, c2, t2, l2 = symbols("k2 c2 t2 l2")
c_ost2 = 1000000
am_lst5 = []
c_ost_lst5 = []
for i in range(15):
    Am = (c2 - l2) / t2
    c_ost2 -= Am.subs({c2: 1000000, l2: 0, t2: 15})
    am_lst5.append(round(Am.subs({c2: 1000000, l2: 0, t2: 15}), 2))
    c_ost_lst5.append(round(c_ost2, 2))
print("Am_list5", am_lst5)
print("c_ost_list5", c_ost_lst5)

Aj2 = 0
C_ost2 = 1000000
am_lst6 = []
c_ost_lst6 = []
for i in range(15): #Что это деалет? Ответ: создает цикл из 15 итераций
    Am = k2 * 1 / t2 * (c2 - Aj2)
    C_ost2 -= Am.subs({k2: 2, t2: 15, c2: 1000000})
    c_ost_lst6.append(round(C_ost2, 2))
    Aj2 += Am
    am_lst6.append(round(Am.subs({k2: 2, t2: 15, c2: 1000000}), 2))
print("Am_lst6:", am_lst6)
print("c_ost_lst6:", c_ost_lst6)
# Создание таблиц
print("")
Y = range(1, 16)
table3 = zip(Y, am_lst5, c_ost_lst5)
table4 = zip(Y, am_lst6, c_ost_lst6)
tframe3 = pd.DataFrame(table3, columns=["Y", "am_lst5", "c_ost_lst5"]) #Что это делает? Ответ: создает таблицу
tframe4 = pd.DataFrame(table4, columns=["Y", "am_lst6", "c_ost_lst6"])
print(tframe3)
print(tframe4)

# Визуализация
plt.figure()
plt.plot(tframe3["Y"], tframe3["c_ost_lst5"], label="Линейная аммортизация")
plt.ylabel("Остаточная стоимость")
plt.xlabel("Год")
plt.savefig("picture13.png")

plt.figure()
plt.plot(tframe4["Y"], tframe4["c_ost_lst6"], label="Ускоренная аммортизация")
plt.ylabel("Остаточнаяz стоимость")
plt.xlabel("Год")
plt.savefig("picture14.png")

vals3 = am_lst5
labels = [str(x) for x in range(1, 16)]
explode = [0.1] * 15 #Что это делает? Ответ: создание списка с отступами между частями круговой диаграммы 
fig, ax = plt.subplots()
plt.pie(
    vals3,
    labels=labels,
    explode=explode,
    autopct="%1.1f%%",
    shadow=True,
    wedgeprops={"lw": 1, "ls": "-", "edgecolor": "k"},
    rotatelabels=False,
)
ax.axis("equal")
plt.savefig("picture15.png")

vals4 = am_lst6
labels2 = [str(x) for x in range(1, 16)]
fig, ax = plt.subplots()
plt.pie(
    vals4,
    labels=labels,
    explode=explode,
    autopct="%1.1f%%",
    shadow=True,
    wedgeprops={"lw": 1, "ls": "-", "edgecolor": "k"},
    rotatelabels=False,
)
plt.savefig("picture16.png")

fig, ax = plt.subplots()
plt.bar(tframe3["Y"], tframe3["am_lst5"])
plt.savefig("picture17.png")

fig, ax = plt.subplots()
plt.bar(tframe4["Y"], tframe4["am_lst6"])
plt.savefig("picture18.png")

#Задание 4 Кобозев Приходько
#Строки 207, 220, 240. Все ответы правильные 5 (Оценил Кобозев А.Д.) 
