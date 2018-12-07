import sys
import asyncio
from os import path

import aiofiles
import yaml
from aiohttp import web, ClientSession


class Server:
    def __init__(self, port=8080, directory="directory", servers=(), save_local=False):
        """

        :param port: порт, на котором надо запустить сервер
        :param directory: директория с файлами
        :param servers: остальные ноды
        :param save_local: Нужно ли сохранять файлы локально
        """

        self.port = port

        if not path.isdir(directory):
            raise NotADirectoryError("{} is not a directory".format(directory))

        self.directory = directory

        self.servers = servers

        self.save_local = save_local

    async def search_file_local(self, request):
        """
        Поиск файла в локальном хранилище, без запроса на сторонние сервера
        """
        file_name = request.match_info.get('file_name')
        file_path = path.join(self.directory, file_name)

        if path.isfile(file_path):
            async with aiofiles.open(file_path, mode='r') as f:
                file_text = await f.read()
                return web.Response(text=file_text)
        return web.Response(status=404)

    async def get(self, _server, _file_name):
        """
        Получение информации о файле с сервера
        :param _server: сервер
        :param _file_name: имя файла
        :return: содержание файла или None
        """
        url = "/".join([_server, "local", _file_name])
        async with ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    return await resp.text()

    async def get_remote_information(self, file_name):
        """
        Запрос получение информации о содержании недоступого на сервере файла
        :param file_name: название файла
        :return: Содержимое файла или None
        """
        tasks = []

        for server in self.servers:
            tasks.append(self.get(server, file_name))

        file_data, _ = await asyncio.wait(tasks)

        return file_data.pop().result()

    async def get_file(self, request):
        file_name = request.match_info.get('file_name')
        file_path = path.join(self.directory, file_name)

        if path.isfile(file_path):
            async with aiofiles.open(file_path, mode='r') as f:
                file_text = await f.read()
                return web.Response(text=file_text)

        else:
            file_data = await self.get_remote_information(file_name)

            if file_data is not None:
                if self.save_local:
                    async with aiofiles.open(file_name, "w") as out:
                        await out.write(file_data)
                return web.Response(text=file_data)
            else:
                return web.Response(status=404)

    def run(self):
        """
        Запуск сервера
        """
        app = web.Application()
        app.add_routes([
            web.get("/{file_name}", self.get_file),
            web.get("/local/{file_name}", self.search_file_local)
        ])
        web.run_app(app, port=self.port)


if __name__ == '__main__':
    config_file = f"configuration_files/configuration{sys.argv[1]}.yaml"
    with open(config_file, 'r') as stream:
        params = yaml.load(stream)
        server = Server(**params)
        server.run()
