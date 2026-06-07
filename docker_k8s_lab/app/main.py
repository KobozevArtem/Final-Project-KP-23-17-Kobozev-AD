# ==============================
# БЛОК 1. ПОДКЛЮЧЕНИЕ БИБЛИОТЕК
# ==============================

from flask import Flask, jsonify, render_template_string, request
import ipaddress
import random
import json
import os
from datetime import datetime
import threading

# Импортируем генератор IP-адресов и таблицу доверенных IP.
from Generator_IP import random_IP, df_good_valid_ip

# Импортируем итоговую функцию проверки IP, URL и HTTPS.
from Container_mod import final_check

# Импортируем Prometheus-сервер и счётчик метрик.
from prometheus_client import start_http_server, Counter


# ==============================
# БЛОК 2. НАСТРОЙКА PROMETHEUS-МЕТРИК
# ==============================

def start_prometheus():
    """
    Запускает отдельный HTTP-сервер Prometheus на порту 8000.
    Prometheus обращается к этому порту и собирает метрики приложения.
    """

    start_http_server(8000)


# Запускаем Prometheus-сервер в отдельном daemon-потоке.
# Это позволяет одновременно работать Flask-приложению и серверу метрик.
threading.Thread(target=start_prometheus, daemon=True).start()

# Создаём счётчик проверок IP.
# Метка status принимает значения allowed или denied.
ip_checks_total = Counter(
    "ip_checks_total",
    "Total number of IP checks",
    ["status"]
)


# ==============================
# БЛОК 3. НАСТРОЙКА FLASK-ПРИЛОЖЕНИЯ
# ==============================

# Создаём экземпляр Flask-приложения.
app = Flask(__name__)

# Отключаем ASCII-экранирование, чтобы русские символы корректно отображались в JSON.
app.json.ensure_ascii = False

# Имя файла, в котором хранится журнал заблокированных соединений.
BLOCKED_FILE = "blocked_list.json"

# Формируем множество доверенных IP-адресов.
# Используется set, потому что проверка принадлежности в множестве выполняется быстро.
good_ip = {
    ipaddress.ip_address(i)
    for i in df_good_valid_ip["IP"].values
}

# Список URL для генерации тестовых соединений.
# В списке есть корректные HTTPS-адреса, небезопасный HTTP и URL без схемы.
URLS = [
    "https://bank.example.ru",
    "https://api.bank.example.ru",
    "http://bank.example.ru",
    "bank.example.ru"
]


# ==============================
# БЛОК 4. РАБОТА С ЖУРНАЛОМ БЛОКИРОВОК
# ==============================

def load_blocked_list():
    """
    Загружает журнал заблокированных соединений из JSON-файла.
    Если файл отсутствует или повреждён, возвращается пустой список.
    """

    # Если файл журнала ещё не создан, возвращаем пустой список.
    if not os.path.exists(BLOCKED_FILE):
        return []

    try:
        # Открываем JSON-файл и читаем список заблокированных соединений.
        with open(BLOCKED_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    except json.JSONDecodeError:
        # Если файл существует, но JSON повреждён, возвращаем пустой список.
        return []


def save_blocked_list(blocked_list):
    """
    Сохраняет журнал заблокированных соединений в JSON-файл.
    """

    with open(BLOCKED_FILE, "w", encoding="utf-8") as file:
        # ensure_ascii=False нужен для корректного сохранения русского текста.
        # indent=4 делает файл читаемым.
        json.dump(blocked_list, file, ensure_ascii=False, indent=4)


def is_blocked(ip, url):
    """
    Проверяет, был ли ранее заблокирован конкретный IP и URL.
    """

    blocked_list = load_blocked_list()

    # Ищем совпадение по IP и URL.
    for item in blocked_list:
        if item["ip"] == ip and item["url"] == url:
            return True

    return False


# ==============================
# БЛОК 5. ГЕНЕРАЦИЯ И ПРОВЕРКА СОЕДИНЕНИЙ
# ==============================

def generate_check_results():
    """
    Формирует таблицу из 10 соединений.
    Для каждого соединения выбирается случайный IP и URL,
    затем выполняется проверка через final_check().
    """

    results = []

    for i in range(1, 11):
        # Получаем случайный IP и его тип из Generator_IP.py.
        row_ip, ip_type = random_IP()

        # Выбираем случайный URL из списка URLS.
        url = random.choice(URLS)

        # Если IP и URL уже были добавлены оператором в журнал блокировок,
        # соединение сразу считается запрещённым.
        if is_blocked(row_ip, url):
            reason = "Соединение заблокировано оператором ранее"
            permission = False

        else:
            # Если записи нет в журнале, выполняем полную проверку IP и HTTPS.
            reason, permission = final_check(url, row_ip, good_ip)

        # Увеличиваем счётчик Prometheus.
        # Если соединение разрешено, увеличиваем status="allowed".
        # Если запрещено, увеличиваем status="denied".
        if permission:
            ip_checks_total.labels(status="allowed").inc()
        else:
            ip_checks_total.labels(status="denied").inc()

        # Добавляем результат проверки в общий список.
        results.append({
            "conn_num": i,
            "ip": row_ip,
            "url": url,
            "type": ip_type,
            "permission": permission,
            "reason": reason
        })

    # Подсчитываем количество разрешённых соединений.
    allowed = len([r for r in results if r["permission"]])

    # Подсчитываем количество запрещённых соединений.
    denied = len(results) - allowed

    # Формируем словарь распределения IP по типам.
    type_counts = {}

    for row in results:
        type_counts[row["type"]] = type_counts.get(row["type"], 0) + 1

    return results, allowed, denied, type_counts


# ==============================
# БЛОК 6. ГЛАВНАЯ СТРАНИЦА ВЕБ-ИНТЕРФЕЙСА
# ==============================

@app.route("/")
def index():
    """
    Главная страница приложения.
    Отображает:
    - таблицу текущих проверок;
    - статистику разрешённых и запрещённых соединений;
    - журнал блокировок;
    - графики Chart.js.
    """

    # Получаем новые результаты проверок.
    results, allowed, denied, type_counts = generate_check_results()

    # Загружаем журнал заблокированных соединений.
    blocked_list = load_blocked_list()

    # HTML-шаблон интерфейса.
    # render_template_string используется для хранения шаблона прямо внутри main.py.
    html = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Security Container</title>

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #0f172a;
            color: white;
            padding: 30px;
            margin: 0;
        }

        h1, h2 {
            color: #38bdf8;
        }

        .subtitle {
            color: #cbd5e1;
            margin-bottom: 25px;
        }

        .stats {
            display: flex;
            gap: 15px;
            margin-bottom: 25px;
            flex-wrap: wrap;
        }

        .card {
            padding: 18px 28px;
            background-color: #1e293b;
            border-radius: 12px;
            font-size: 18px;
            min-width: 180px;
        }

        .refresh-btn {
            margin-bottom: 25px;
            padding: 12px 22px;
            background: #22c55e;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            color: white;
            font-size: 16px;
            font-weight: bold;
        }

        table {
            border-collapse: collapse;
            width: 100%;
            margin-top: 20px;
            background-color: #111827;
        }

        th, td {
            border: 1px solid #334155;
            padding: 10px;
            text-align: center;
            font-size: 14px;
        }

        th {
            background-color: #1e293b;
            color: #e2e8f0;
        }

        .true {
            color: #22c55e;
            font-weight: bold;
        }

        .false {
            color: #ef4444;
            font-weight: bold;
        }

        .block-btn {
            padding: 8px 12px;
            background: #ef4444;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            color: white;
            font-weight: bold;
        }

        .block-btn:disabled {
            background: #64748b;
            cursor: not-allowed;
        }

        .charts {
            margin-top: 50px;
            display: flex;
            flex-direction: column;
            gap: 35px;
        }

        .chart-box {
            background: white;
            border-radius: 15px;
            padding: 25px;
            color: black;
            width: 100%;
            max-width: 1000px;
        }

        canvas {
            width: 100% !important;
            height: 420px !important;
        }

        #toast {
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: #22c55e;
            color: white;
            padding: 15px 22px;
            border-radius: 8px;
            display: none;
            z-index: 1000;
        }
    </style>
</head>

<body>

<h1>Контейнер безопасности</h1>
<p class="subtitle">Проверка IP-адресов и URL-схемы соединения</p>

<div class="stats">
    <div class="card">✅ Разрешено: {{ allowed }}</div>
    <div class="card">❌ Запрещено: {{ denied }}</div>
    <div class="card">🔎 Всего проверок: {{ results|length }}</div>
    <div class="card">
        🚫 В журнале блокировок:
        <span id="blocked-counter">{{ blocked_list|length }}</span>
    </div>
</div>

<form method="get">
    <button class="refresh-btn" type="submit">🔄 Обновить данные</button>
</form>

<table>
    <tr>
        <th>#</th>
        <th>IP</th>
        <th>URL</th>
        <th>Тип IP</th>
        <th>Решение</th>
        <th>Причина</th>
        <th>Действие</th>
    </tr>

    {% for row in results %}
    <tr>
        <td>{{ row.conn_num }}</td>
        <td>{{ row.ip }}</td>
        <td>{{ row.url }}</td>
        <td>{{ row.type }}</td>

        <td class="{% if row.permission %}true{% else %}false{% endif %}">
            {{ row.permission }}
        </td>

        <td>{{ row.reason }}</td>

        <td>
            <button class="block-btn"
                    type="button"
                    onclick="blockConnection(this, '{{ row.ip }}', '{{ row.url }}', '{{ row.type }}', '{{ row.reason }}')">
                🚫 Заблокировать
            </button>
        </td>
    </tr>
    {% endfor %}
</table>

<h2>Журнал заблокированных соединений</h2>

<div id="blocked-container">
    {% if blocked_list %}
    <table id="blocked-table">
        <tr>
            <th>#</th>
            <th>IP</th>
            <th>URL</th>
            <th>Тип IP</th>
            <th>Причина блокировки</th>
            <th>Дата и время блокировки</th>
        </tr>

        {% for item in blocked_list %}
        <tr>
            <td>{{ loop.index }}</td>
            <td>{{ item.ip }}</td>
            <td>{{ item.url }}</td>
            <td>{{ item.type }}</td>
            <td>{{ item.reason }}</td>
            <td>{{ item.blocked_at }}</td>
        </tr>
        {% endfor %}
    </table>
    {% else %}
    <p id="empty-blocked-list">Пока нет заблокированных соединений.</p>
    {% endif %}
</div>

<div class="charts">
    <div class="chart-box">
        <h3>Количество разрешённых и запрещённых соединений</h3>
        <canvas id="barChart"></canvas>
    </div>

    <div class="chart-box">
        <h3>Распределение типов IP-адресов</h3>
        <canvas id="pieChart"></canvas>
    </div>
</div>

<div id="toast"></div>

<script>
    // ==============================
    // БЛОК JS 1. ПЕРЕДАЧА ДАННЫХ ИЗ FLASK В JAVASCRIPT
    // ==============================

    const allowed = {{ allowed }};
    const denied = {{ denied }};
    const typeCounts = {{ type_counts | tojson }};


    // ==============================
    // БЛОК JS 2. ПОСТРОЕНИЕ ГИСТОГРАММЫ
    // ==============================

    new Chart(document.getElementById('barChart'), {
        type: 'bar',
        data: {
            labels: ['Разрешено', 'Запрещено'],
            datasets: [{
                label: 'Количество соединений',
                data: [allowed, denied],
                backgroundColor: ['#22c55e', '#ef4444']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });


    // ==============================
    // БЛОК JS 3. ПОСТРОЕНИЕ КРУГОВОЙ ДИАГРАММЫ
    // ==============================

    const typeColors = {
        'Private_IP': '#22c55e',
        'Trash_IP': '#ef4444',
        'Trust_IP': '#facc15',
        'Untrust_IP': '#38bdf8',
        'Special_IP': '#a78bfa'
    };

    new Chart(document.getElementById('pieChart'), {
        type: 'pie',
        data: {
            labels: Object.keys(typeCounts),
            datasets: [{
                data: Object.values(typeCounts),
                backgroundColor: Object.keys(typeCounts).map(k => typeColors[k] || '#94a3b8')
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });


    // ==============================
    // БЛОК JS 4. ВСПЛЫВАЮЩЕЕ УВЕДОМЛЕНИЕ
    // ==============================

    function showToast(message) {
        const toast = document.getElementById("toast");
        toast.innerText = message;
        toast.style.display = "block";

        setTimeout(() => {
            toast.style.display = "none";
        }, 3000);
    }


    // ==============================
    // БЛОК JS 5. ДОБАВЛЕНИЕ IP И URL В ЖУРНАЛ БЛОКИРОВОК
    // ==============================

    function blockConnection(button, ip, url, type, reason) {
        fetch('/block', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                ip: ip,
                url: url,
                type: type,
                reason: reason
            })
        })
        .then(response => response.json())
        .then(data => {
            showToast(data.message);

            // Если запись успешно добавлена, она сразу появляется в журнале без обновления страницы.
            if (data.status === "success") {
                addBlockedRow(data.item);
                updateBlockedCounter();

                button.disabled = true;
                button.innerText = "Уже заблокировано";
            }

            // Если запись уже была в журнале, повторное добавление не выполняется.
            if (data.status === "exists") {
                button.disabled = true;
                button.innerText = "Уже заблокировано";
            }
        })
        .catch(error => {
            showToast('Ошибка при добавлении в журнал блокировок');
            console.error(error);
        });
    }


    // ==============================
    // БЛОК JS 6. ДОБАВЛЕНИЕ СТРОКИ В ТАБЛИЦУ ЖУРНАЛА
    // ==============================

    function addBlockedRow(item) {
        const emptyMessage = document.getElementById("empty-blocked-list");

        if (emptyMessage) {
            emptyMessage.remove();
        }

        let table = document.getElementById("blocked-table");

        if (!table) {
            const container = document.getElementById("blocked-container");

            table = document.createElement("table");
            table.id = "blocked-table";

            table.innerHTML = `
                <tr>
                    <th>#</th>
                    <th>IP</th>
                    <th>URL</th>
                    <th>Тип IP</th>
                    <th>Причина блокировки</th>
                    <th>Дата и время блокировки</th>
                </tr>
            `;

            container.appendChild(table);
        }

        const rowNumber = table.rows.length;
        const row = table.insertRow(-1);

        row.innerHTML = `
            <td>${rowNumber}</td>
            <td>${escapeHtml(item.ip)}</td>
            <td>${escapeHtml(item.url)}</td>
            <td>${escapeHtml(item.type)}</td>
            <td>${escapeHtml(item.reason)}</td>
            <td>${escapeHtml(item.blocked_at)}</td>
        `;
    }


    // ==============================
    // БЛОК JS 7. ОБНОВЛЕНИЕ СЧЁТЧИКА ЖУРНАЛА
    // ==============================

    function updateBlockedCounter() {
        const counter = document.getElementById("blocked-counter");

        if (counter) {
            const current = parseInt(counter.textContent, 10);
            counter.textContent = current + 1;
        }
    }


    // ==============================
    // БЛОК JS 8. ЗАЩИТА HTML-ВЫВОДА
    // ==============================

    function escapeHtml(value) {
        if (value === null || value === undefined) {
            return "";
        }

        return String(value)
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#039;");
    }
</script>

</body>
</html>
    """

    # Передаём данные из Python в HTML-шаблон.
    return render_template_string(
        html,
        results=results,
        allowed=allowed,
        denied=denied,
        type_counts=type_counts,
        blocked_list=blocked_list
    )


# ==============================
# БЛОК 7. API ДОБАВЛЕНИЯ В ЖУРНАЛ БЛОКИРОВОК
# ==============================

@app.route("/block", methods=["POST"])
def block():
    """
    API-метод добавляет IP и URL в журнал блокировок.
    Вызывается из JavaScript через fetch().
    """

    # Получаем JSON-данные из POST-запроса.
    data = request.get_json()

    ip = data.get("ip")
    url = data.get("url")
    ip_type = data.get("type")
    reason = data.get("reason")

    # Проверяем, что обязательные данные были переданы.
    if not ip or not url:
        return jsonify({
            "status": "error",
            "message": "IP или URL не переданы"
        }), 400

    # Формируем запись журнала блокировок.
    blocked_item = {
        "ip": ip,
        "url": url,
        "type": ip_type,
        "reason": reason,
        "blocked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Загружаем текущий журнал блокировок.
    blocked_list = load_blocked_list()

    # Проверяем, нет ли уже такой записи в журнале.
    for item in blocked_list:
        if item["ip"] == ip and item["url"] == url:
            return jsonify({
                "status": "exists",
                "message": f"IP {ip} и URL {url} уже есть в журнале блокировок",
                "item": item
            })

    # Добавляем новую запись в журнал.
    blocked_list.append(blocked_item)

    # Сохраняем обновлённый журнал в JSON-файл.
    save_blocked_list(blocked_list)

    return jsonify({
        "status": "success",
        "message": f"IP {ip} и URL {url} добавлены в журнал блокировок",
        "item": blocked_item
    })


# ==============================
# БЛОК 8. API ПОЛУЧЕНИЯ РЕЗУЛЬТАТОВ ПРОВЕРКИ
# ==============================

@app.route("/check")
def check():
    """
    API-метод возвращает результаты новых проверок в формате JSON.
    Может использоваться для внешней интеграции или тестирования.
    """

    results, allowed, denied, type_counts = generate_check_results()

    return jsonify({
        "allowed": allowed,
        "denied": denied,
        "type_counts": type_counts,
        "results": results,
        "blocked_list": load_blocked_list()
    })


# ==============================
# БЛОК 9. API ПОЛУЧЕНИЯ ЖУРНАЛА БЛОКИРОВОК
# ==============================

@app.route("/blocked")
def blocked():
    """
    API-метод возвращает текущий журнал заблокированных соединений.
    """

    return jsonify(load_blocked_list())


# ==============================
# БЛОК 10. ЗАПУСК ПРИЛОЖЕНИЯ
# ==============================

if __name__ == "__main__":
    # Запускаем Flask-сервер на всех сетевых интерфейсах контейнера.
    # Порт 5000 используется Nginx для проксирования запросов.
    app.run(host="0.0.0.0", port=5000)
