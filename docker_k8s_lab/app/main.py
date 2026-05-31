from flask import Flask, jsonify, render_template_string, request
import ipaddress
import random
import json
import os
from datetime import datetime
from Generator_IP import random_IP, df_good_valid_ip
from Container_mod import final_check
from prometheus_client import start_http_server, Counter
import threading


# ---------------- Prometheus ----------------

def start_prometheus():
    start_http_server(8000)


threading.Thread(target=start_prometheus, daemon=True).start()

ip_checks_total = Counter(
    "ip_checks_total",
    "Total number of IP checks",
    ["status"]
)


# ---------------- Flask ----------------

app = Flask(__name__)
app.json.ensure_ascii = False

BLOCKED_FILE = "blocked_list.json"

good_ip = {
    ipaddress.ip_address(i)
    for i in df_good_valid_ip["IP"].values
}

URLS = [
    "https://bank.example.ru",
    "https://api.bank.example.ru",
    "http://bank.example.ru",
    "bank.example.ru"
]


# ---------------- Работа с журналом блокировок ----------------

def load_blocked_list():
    if not os.path.exists(BLOCKED_FILE):
        return []

    try:
        with open(BLOCKED_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return []


def save_blocked_list(blocked_list):
    with open(BLOCKED_FILE, "w", encoding="utf-8") as file:
        json.dump(blocked_list, file, ensure_ascii=False, indent=4)


def is_blocked(ip, url):
    blocked_list = load_blocked_list()

    for item in blocked_list:
        if item["ip"] == ip and item["url"] == url:
            return True

    return False


# ---------------- Генерация проверок ----------------

def generate_check_results():
    results = []

    for i in range(1, 11):
        row_ip, ip_type = random_IP()
        url = random.choice(URLS)

        if is_blocked(row_ip, url):
            reason = "Соединение заблокировано оператором ранее"
            permission = False
        else:
            reason, permission = final_check(url, row_ip, good_ip)

        if permission:
            ip_checks_total.labels(status="allowed").inc()
        else:
            ip_checks_total.labels(status="denied").inc()

        results.append({
            "conn_num": i,
            "ip": row_ip,
            "url": url,
            "type": ip_type,
            "permission": permission,
            "reason": reason
        })

    allowed = len([r for r in results if r["permission"]])
    denied = len(results) - allowed

    type_counts = {}
    for row in results:
        type_counts[row["type"]] = type_counts.get(row["type"], 0) + 1

    return results, allowed, denied, type_counts


# ---------------- Главная страница ----------------

@app.route("/")
def index():
    results, allowed, denied, type_counts = generate_check_results()
    blocked_list = load_blocked_list()

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

h1 {
    color: #38bdf8;
    margin-bottom: 5px;
}

h2 {
    color: #38bdf8;
    margin-top: 45px;
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
    box-shadow: 0 4px 10px rgba(0,0,0,0.25);
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

.refresh-btn:hover {
    background: #16a34a;
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

.block-btn:hover {
    background: #dc2626;
}

.block-btn:disabled {
    background: #64748b;
    cursor: not-allowed;
}

.blocked-table {
    margin-top: 20px;
}

.empty-list {
    color: #cbd5e1;
    margin-top: 15px;
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

.chart-title {
    font-size: 20px;
    font-weight: bold;
    margin-bottom: 20px;
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
    font-size: 16px;
    box-shadow: 0 0 12px rgba(0,0,0,0.4);
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
    <div class="card">🚫 В журнале блокировок: <span id="blocked-counter">{{ blocked_list|length }}</span></div>
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
<table id="blocked-table" class="blocked-table">
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
<p id="empty-blocked-list" class="empty-list">Пока нет заблокированных соединений.</p>
{% endif %}
</div>

<div class="charts">
    <div class="chart-box">
        <div class="chart-title">📊 Количество разрешённых и запрещённых соединений</div>
        <canvas id="barChart"></canvas>
    </div>

    <div class="chart-box">
        <div class="chart-title">🥧 Распределение типов IP-адресов</div>
        <canvas id="pieChart"></canvas>
    </div>
</div>

<div id="toast"></div>

<script>
const allowed = {{ allowed }};
const denied = {{ denied }};
const typeCounts = {{ type_counts | tojson }};

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
        maintainAspectRatio: false,
        plugins: {
            legend: {
                labels: {
                    usePointStyle: true
                }
            }
        }
    }
});

function showToast(message) {
    const toast = document.getElementById("toast");
    toast.innerText = message;
    toast.style.display = "block";

    setTimeout(() => {
        toast.style.display = "none";
    }, 3000);
}

function blockConnection(button, ip, url, type, reason) {
    fetch('/block', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache'
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

        if (data.status === "success") {
            addBlockedRow(data.item);
            updateBlockedCounter();

            button.disabled = true;
            button.innerText = "Уже заблокировано";
        }

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
        table.className = "blocked-table";

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

function updateBlockedCounter() {
    const counter = document.getElementById("blocked-counter");

    if (counter) {
        const current = parseInt(counter.textContent, 10);
        counter.textContent = current + 1;
    }
}

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

    return render_template_string(
        html,
        results=results,
        allowed=allowed,
        denied=denied,
        type_counts=type_counts,
        blocked_list=blocked_list
    )


# ---------------- API: добавление в журнал ----------------

@app.route("/block", methods=["POST"])
def block():
    data = request.get_json()

    ip = data.get("ip")
    url = data.get("url")
    ip_type = data.get("type")
    reason = data.get("reason")

    if not ip or not url:
        return jsonify({
            "status": "error",
            "message": "IP или URL не переданы"
        }), 400

    blocked_item = {
        "ip": ip,
        "url": url,
        "type": ip_type,
        "reason": reason,
        "blocked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    blocked_list = load_blocked_list()

    for item in blocked_list:
        if item["ip"] == ip and item["url"] == url:
            return jsonify({
                "status": "exists",
                "message": f"IP {ip} и URL {url} уже есть в журнале блокировок",
                "item": item
            })

    blocked_list.append(blocked_item)
    save_blocked_list(blocked_list)

    return jsonify({
        "status": "success",
        "message": f"IP {ip} и URL {url} добавлены в журнал блокировок",
        "item": blocked_item
    })


# ---------------- API: проверка ----------------

@app.route("/check")
def check():
    results, allowed, denied, type_counts = generate_check_results()

    return jsonify({
        "allowed": allowed,
        "denied": denied,
        "type_counts": type_counts,
        "results": results,
        "blocked_list": load_blocked_list()
    })


@app.route("/blocked")
def blocked():
    return jsonify(load_blocked_list())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)