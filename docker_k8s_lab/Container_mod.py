import ipaddress


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

    return "Соединение разрешено: IP доверенный, используется HTTPS", True
