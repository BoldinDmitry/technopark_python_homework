import argparse
import pickle
import socket
import uuid
import os
import time


class QueuePathException(Exception):
    """
    Исключение, если директория переданная при запуске не найдена
    """
    pass


class NotTaskError(Exception):
    """
    Исключение, которое выбрасывается, когда в put_new_task передается не Task
    """
    pass


class QueueOfTasks:
    """
    Кастомная очередь, умеет работать только с объектами типа Task
    """
    def __init__(self):
        self.tasks = []

    def get_task_for_work(self):
        """
        Получить новое задание из очереди

        :return: ID задания и текст задания
        """
        for task in self.tasks:
            if not task.is_in_work:
                task.taken_for_work()
                return task.id, task.data

    def task_is_done(self, task_id):
        """
        Пометить, что задание сделано

        :param task_id: ID сделанного задания
        :return: NO или YES в зависисмости от корректности запроса
        """
        for i in range(len(self.tasks)):
            if self.tasks[i].id == task_id and self.tasks[i].is_in_work:
                del self.tasks[i]
                return "YES"
        return "NO"

    def find(self, task_id):
        """
        Поиск задания в очереди

        :param task_id: ID задания, которое нужно найти
        :return: YES или NO в зависимости от нахождения объекта в очереди
        """
        for i in range(len(self.tasks)):
            if self.tasks[i].id == task_id:
                return "YES"
        return "NO"

    def put(self, task):
        """
        Положить в очередь объект типа Task

        :param task: Задание, которое надо добавить в очередь
        :return: None, если всё прошло штатно или бросает ошибку
        """
        if isinstance(task, Task):
            self.tasks.append(task)
        else:
            raise NotTaskError

    def __str__(self):
        return str(self.tasks)


class Task:
    def __init__(self, data, timeout):
        self._data = data
        self._timeout = timeout

        self._id = None
        self.generate_id()

        self._is_in_work_since = 0

    def generate_id(self):
        self._id = str(uuid.uuid4())

    @property
    def id(self):
        return self._id

    @property
    def data(self):
        return self._data

    @property
    def is_in_work(self):
        """
        В работе ли задание
        """
        return self._is_in_work_since + 300 > time.time()

    def taken_for_work(self):
        self._is_in_work_since = time.time()

    def __str__(self):
        return self._data

    def __repr__(self):
        return "Task({} {})".format(str(self._id), self._data)


class TaskQueueServer:
    def __init__(self, port=None, timeout=None, ip=None, path=None):

        self._port = port if port is not None else 5555
        self._ip = ip if ip is not None else "127.0.0.1"
        self._timeout = timeout if timeout is not None else 300

        self._path = path
        if not os.path.isdir(path):
            raise QueuePathException

        self._queues = {}
        self.load_queues()

        self._connection = None

    def load_queues(self):
        """
        Загрузка последнего состояния из файла при загрузке
        """
        if os.path.isfile(self._path + 'queues.pickle'):
            with open(self._path + 'queues.pickle', 'rb') as handle:
                self._queues = pickle.load(handle)

    def make_server(self):
        self._connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._connection.bind((self._ip, self._port))
        self._connection.listen(100)

    def add_task(self, queue, data):
        """
        Добавление нового задания в очередь
        """
        if queue not in self._queues:
            self._queues[queue] = QueueOfTasks()

        task = Task(data, self._timeout)

        self._queues[queue].put(task)

        return task.id

    def save_queues(self):
        """
        Сохранить текущее состаяние очереди в файл
        """
        with open(self._path + 'queues.pickle', 'wb') as handle:
            pickle.dump(
                self._queues,
                handle
            )

    def run(self):

        self.make_server()

        while True:
            current_connection, address = self._connection.accept()

            raw_data = current_connection.recv(100)
            parsed_data = raw_data.split()
            method = parsed_data[0]
            del parsed_data[0]

            if method == b"ADD":

                queue, length, data = parsed_data
                queue, length, data = queue.decode("utf"), int(length), data.decode("utf")

                if length > len(data):
                    big_data = current_connection.recv(length - len(data))
                    data += big_data.decode("utf")

                task_id = self.add_task(str(queue), str(data))

                current_connection.send(task_id.encode("utf"))

            elif method == b"GET":
                queue = parsed_data[0].decode("utf")

                if queue not in self._queues:
                    current_connection.send(b"NONE")

                else:
                    _id, _data = self._queues[queue].get_task_for_work()

                    data = "{} {} {}".format(_id, len(_data), _data)
                    data = data.encode('utf')
                    current_connection.send(data)

            elif method == b"ACK":
                queue, _id = parsed_data
                queue, _id = queue.decode("utf"), _id.decode("utf")

                if queue not in self._queues:
                    current_connection.send(b"NO")

                else:

                    current_connection.send(
                        self._queues[queue].task_is_done(_id).encode("utf")
                    )

            elif method == b"IN":
                queue, _id = parsed_data
                queue, _id = queue.decode("utf"), _id.decode("utf")

                if queue not in self._queues:
                    current_connection.send(b"NO")

                else:
                    current_connection.send(
                        self._queues[queue].find(_id).encode("utf")
                    )

            elif method == b"SAVE":
                self.save_queues()
                current_connection.send(b"OK")

            else:
                current_connection.send(b"ERROR")

            current_connection.close()


def parse_args():
    parser = argparse.ArgumentParser(description='This is a simple task queue server with custom protocol')
    parser.add_argument(
        '-p',
        action="store",
        dest="port",
        type=int,
        default=5555,
        help='Server port')
    parser.add_argument(
        '-i',
        action="store",
        dest="ip",
        type=str,
        default='0.0.0.0',
        help='Server ip adress')
    parser.add_argument(
        '-c',
        action="store",
        dest="path",
        type=str,
        default='./',
        help='Server checkpoints dir')
    parser.add_argument(
        '-t',
        action="store",
        dest="timeout",
        type=int,
        default=300,
        help='Task maximum GET timeout in seconds')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    server = TaskQueueServer(**args.__dict__)
    server.run()
