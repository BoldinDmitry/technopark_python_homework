import re
import collections


def parse_log(log, ignore_www):
    """
    Переводит лог, представляющий собой строку в словарь
    :param log: строка лога
    :param ignore_www: надо ли убирать www?
    :return:
    """
    cleared_log = log.strip("\n")
    splited_log = cleared_log.split()

    return {
        "request_date": (splited_log[0] + " " + splited_log[1]).strip('[]'),
        "request_type": splited_log[2].strip('"'),
        "request": splited_log[3].replace("www", "") if ignore_www else splited_log[3],
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

    logs = []
    for log in logs_and_rubbish:
        if "http" in log:
            logs.append(parse_log(log, ignore_www))
    return logs


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
        ignore_urls = []

    pretty_logs = get_pretty_logs(ignore_www)
    logs_count = collections.Counter()
    mil_counter = collections.Counter()

    for log in pretty_logs:

        not_in_ignore_urls = log["request"] not in ignore_urls
        is_file = not ignore_files or ("." in log["request"].split("/")[-1])
        right_request_type = (log["request_type"] == request_type) or not request_type

        if not_in_ignore_urls and is_file and right_request_type:

            logs_count[log["request"]] += 1

            if slow_queries:
                mil_counter[log["request"]] += log["response_time"]

    if slow_queries:
        mil_counter, logs_count = mil_counter.most_common(5), logs_count.most_common(5)
        for_return = []
        for i in range(4):
            for_return.append(
                mil_counter[i][1] // logs_count[i][1]
            )
        return for_return

    for_return = list(i[1] for i in logs_count.most_common(5))
    return for_return
