from flask import Flask, jsonify
import ipaddress
import random
from Generator_IP import random_IP, df_good_valid_ip
from Container_mod import final_check

app = Flask(__name__)

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


@app.route("/")
def index():
    return jsonify({
        "service": "Security Container",
        "status": "running",
        "description": "IP and HTTPS validation service"
    })


@app.route("/check")
def check():
    results = []

    for i in range(1, 11):
        row_ip, ip_type = random_IP()
        url = random.choice(URLS)

        reason, permission = final_check(url, row_ip, good_ip)

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

    return jsonify({
        "allowed": allowed,
        "denied": denied,
        "results": results
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
