import argparse
import sys
import re


def output(line):
    print(line)


def check_entry(pattern, line, ignore_case=False):
    """
    Фунция для проерки нахождения шаблона в строке, может игнорировать регистр
    :param ignore_case: игнорировать регистр
    :param pattern: шаблон вхождения
    :param line: строка
    :return: bool переменную, True, если совпадение
    """
    if ignore_case:
        pattern = pattern.lower()
        line = line.lower()

    pattern = pattern.replace("?", ".")
    pattern = pattern.replace("*", "\w*")

    return re.search(pattern, line) is not None


def grep(lines, params):
    count = 0
    last_index = -1
    pattern = params.pattern
    for index, line in enumerate(lines):

        # Проверка на совпадение, включая возможный инверт
        if check_entry(pattern, line, params.ignore_case) != params.invert:

            if not params.count:

                # Определение контекста
                start = max(0, index - params.before_context - params.context, last_index + 1)
                stop = min(len(lines), index + params.after_context + params.context + 1)

                for i in range(start, stop):
                    if params.line_number:

                        # Исключение для случаев, когда есть контекст и необходимо напечать номер
                        if check_entry(pattern, lines[i], params.ignore_case):
                            output(str(i + 1) + ":" + lines[i])
                            last_index = i
                        else:
                            output(str(i + 1) + "-" + lines[i])
                            last_index = i

                    else:
                        output(lines[i])
                        last_index = i

            else:
                count += 1

    # Искоючение для случаев, когда нужно показать только колличество совпадений
    if params.count:
        output(str(count))


def parse_args(args):
    parser = argparse.ArgumentParser(description='This is a simple grep on python')
    parser.add_argument(
        '-v', action="store_true", dest="invert", default=False, help='Selected lines are those not matching pattern.')
    parser.add_argument(
        '-i', action="store_true", dest="ignore_case", default=False, help='Perform case insensitive matching.')
    parser.add_argument(
        '-c',
        action="store_true",
        dest="count",
        default=False,
        help='Only a count of selected lines is written to standard output.')
    parser.add_argument(
        '-n',
        action="store_true",
        dest="line_number",
        default=False,
        help='Each output line is preceded by its relative line number in the file, starting at line 1.')
    parser.add_argument(
        '-C',
        action="store",
        dest="context",
        type=int,
        default=0,
        help='Print num lines of leading and trailing context surrounding each match.')
    parser.add_argument(
        '-B',
        action="store",
        dest="before_context",
        type=int,
        default=0,
        help='Print num lines of trailing context after each match')
    parser.add_argument(
        '-A',
        action="store",
        dest="after_context",
        type=int,
        default=0,
        help='Print num lines of leading context before each match.')
    parser.add_argument('pattern', action="store", help='Search pattern. Can contain magic symbols: ?*')
    return parser.parse_args(args)


def main():
    params = parse_args(sys.argv[1:])
    grep(sys.stdin.readlines(), params)


if __name__ == '__main__':
    main()
