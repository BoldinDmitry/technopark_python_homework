import re
import collections

from urllib.parse import urlparse
from datetime import datetime


def parse_log(log, ignore_www):
    """
    Переводит лог, представляющий собой строку в словарь
    :param log: строка лога
    :param ignore_www: надо ли убирать www?
    :return:
    """
    cleared_log = log.strip("\n")
    splited_log = cleared_log.split()

    request = urlparse(splited_log[3])
    # Не использую стандартное проебразование к урлу, тк нужно будет потом удалять http\w?://
    request = "{}{}".format(request.netloc, request.path)
    if ignore_www and request.startswith("www."):
        request = request[4:]

    date_str = (splited_log[0] + " " + splited_log[1]).strip('[]')
    return {
        "request_date": datetime.strptime(date_str, "%d/%b/%Y %H:%M:%S"),
        "request_type": splited_log[2].strip('"'),
        "request": request,
        "protocol": splited_log[4].strip('"'),
        "response_code": int(splited_log[5]),
        "response_time": int(splited_log[6])
    }


def get_pretty_logs(ignore_www):
    """
    Функция для считывания из файла логов и приведения их листу словарей
    :param ignore_www: нужно ли убирать www из ссылки
    :return: лист словарей
    """
    log_file = open("log.log")
    logs_and_rubbish = log_file.readlines()
    regex = re.compile(r'\[\d*\/\w*\/\w* \w*:\w*:\w*\] "\w* http\w?:\/\/\S* \S*" \d* \d*')
    parsed_logs = []
    for log in logs_and_rubbish:
        if re.match(regex, log):
            parsed_logs.append(parse_log(log, ignore_www))
    return parsed_logs


def parse(
        ignore_files=False,
        ignore_urls=None,
        start_at=None,
        stop_at=None,
        request_type=None,
        ignore_www=False,
        slow_queries=False
):
    if ignore_urls is None:
        ignore_urls = {}
    else:
        ignore_urls = set(ignore_urls)

    if start_at is not None:
        start_at = datetime.strptime(start_at, "%d/%b/%Y %H:%M:%S")

    if stop_at is not None:
        stop_at = datetime.strptime(stop_at, "%d/%b/%Y %H:%M:%S")

    pretty_logs = get_pretty_logs(ignore_www)
    logs_count = collections.Counter()
    mil_counter = collections.Counter()

    for log in pretty_logs:

        if log["request"] in ignore_urls:
            continue

        if not (not ignore_files or ("." not in log["request"].split("/")[-1])):
            continue

        if not ((log["request_type"] == request_type) or not request_type):
            continue

        # Определние интервала поиска во времени
        start_stop = 1
        if start_at is not None:
            start_stop *= start_at <= log["request_date"]
        if stop_at is not None:
            start_stop *= log["request_date"] <= stop_at

        if start_stop:

            logs_count[log["request"]] += 1

            if slow_queries:
                mil_counter[log["request"]] += log["response_time"]

    if logs_count:
        if slow_queries:

            for i in mil_counter.keys():
                mil_counter[i] //= logs_count[i]
            return [i[1] for i in mil_counter.most_common(5)]

        return [i[1] for i in logs_count.most_common(5)]
    else:
        return []
