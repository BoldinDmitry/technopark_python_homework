class TextHistory:

    def __init__(self):
        self._text = ""
        self._version = 0
        self._actions_list = {}

    @property
    def text(self):
        """
        Геттер текста
        :return: _text
        """
        return self._text

    @property
    def version(self):
        """
        Геттер версии
        :return: _version
        """
        return self._version

    def insert(self, text, pos=None):
        """
        Вставка текста с определнной позиции
        :param text: Текст для вставки
        :param pos: Позиция для вставки (по умолчанию конец строки)
        :return: Номер версии после вставки
        """

        action = InsertAction(
            text=text,
            pos=pos,
            from_version=self._version,
            to_version=self._version + 1
        )
        self._version += 1
        self._text = action.apply(self._text)
        self._actions_list[self._version] = action

        return self._version

    def replace(self, text, pos=None):
        """
        Замена текста
        :param text: Текст, на который нужно заменить
        :param pos: Позиция начала замены (по умолчанию - конец строки)
        :return: Номер версии после замены
        """

        action = ReplaceAction(
            text=text,
            pos=pos,
            from_version=self.version,
            to_version=self.version + 1
        )

        self._version += 1
        self._text = action.apply(self._text)
        self._actions_list[self._version] = action

        return self._version

    def delete(self, pos, length):
        """
        Удаление текста
        :param pos: Позиция начала удаления
        :param length: Сколько символов надо удалить
        :return: Номер версии после удаления
        """

        action = DeleteAction(
            length=length,
            pos=pos,
            from_version=self.version,
            to_version=self.version + 1
        )

        self._version += 1

        self._text = action.apply(self._text)
        self._actions_list[self._version] = action

        return self._version

    def action(self, act):
        """
        Применение действия к текущему тексту и изменение версии
        :param act: Объект класса-наследника от Action
        :return: Новую вересию
        """
        self._text = act.apply(self.text)

        self._version = act.to_version
        self._actions_list[self._version] = act

        return self._version

    @staticmethod
    def _insert_delete_optimization(current_object, next_object):
        """
        Оптимизация для объектов Insert и Delete
        :param current_object: Текущий объект в итерации
        :param next_object: Следующий объект в итерации
        :return: Объект InsertAction или None
        """
        insert_start_pos = current_object.pos
        insert_end_pos = len(current_object.text)
        delete_start_pos = next_object.pos
        delete_end_pos = next_object.pos + next_object.length

        delete_start_in_insert = insert_start_pos <= delete_start_pos <= insert_end_pos
        delete_end_in_insert = insert_start_pos <= delete_end_pos <= insert_end_pos

        if delete_start_in_insert or delete_end_in_insert:
            start = max(insert_start_pos, delete_start_pos)
            s = min(insert_start_pos, delete_start_pos)

            end = min(insert_end_pos, delete_end_pos)

            new_text = current_object.text.replace(current_object.text[start - s:end - s], "")

            return InsertAction(
                text=new_text,
                pos=current_object.pos,
                from_version=current_object.from_version,
                to_version=next_object.to_version
            )

    @staticmethod
    def _double_insert_optimization(current_object, next_object):
        """
        Оптимизация для двух объектов InsertAction
        :param current_object: Текущий объект в итерации
        :param next_object: Следующий объект в итерации
        :return: Объект InsertAction или None, если оптимизацию применить невозможно
        """
        if current_object.pos + len(current_object.text) - next_object.pos == 0:
            return InsertAction(
                text=current_object.text + next_object.text,
                pos=current_object.pos,
                from_version=current_object.from_version,
                to_version=next_object.to_version
            )

    def _make_optimization(self, current_object, next_object):
        """
        Применяет оптимизации к двум объектам, если это возможно
        :param current_object: Текущий объект в итерации
        :param next_object: Следующий объект в итерации
        :return: оптимизацию, если ее возможно сделать, иначе None
        """
        current_is_insert = isinstance(current_object, InsertAction)
        next_is_insert = isinstance(next_object, InsertAction)
        for_return = None
        if current_is_insert and next_is_insert:
            optimization = self._double_insert_optimization(current_object, next_object)
            if optimization is not None:
                for_return = optimization

        next_is_delete = isinstance(next_object, DeleteAction)

        if current_is_insert and next_is_delete:
            optimization = self._insert_delete_optimization(current_object, next_object)
            if optimization is not None:
                for_return = optimization

        return for_return

    def _next_action(self, from_version, to_version):
        from_version = from_version + 1
        to_version = to_version

        for i in range(from_version, to_version):
            if i in self._actions_list.keys():
                yield i

    def get_actions(self, from_version=0, to_version=None):
        """
        Получение объектов всех действий над тестом
        :param from_version: Начиная с версии
        :param to_version: Заканчивая версией
        :return: Список всех объектов
        """
        if to_version is None:
            to_version = len(self._actions_list)

        if from_version > to_version or from_version < 0 or to_version > len(self._actions_list):
            raise ValueError

        for_return = []

        n = self._next_action(from_version, to_version)

        do_nothing = False
        for i in range(from_version, to_version):

            if do_nothing:
                do_nothing = False
                if i != to_version - 1:
                    next(n)
                continue

            if self._actions_list.get(i + 1) is not None:

                current_object = self._actions_list[i + 1]

                if i != to_version - 1:

                    next_index = next(n)
                    next_object = self._actions_list[next_index + 1]

                    optimization = self._make_optimization(current_object, next_object)
                    if optimization is not None:
                        for_return.append(optimization)
                        do_nothing = True
                        continue

                for_return.append(current_object)

        return for_return

    def __repr__(self):
        return "TextHistory({!r}, {!r})".format(self._text, self._version)


class Action:
    def __init__(self, from_version, to_version, pos=None):
        self.new_text = ""
        self._old_text = ""
        self.pos = pos

        self.from_version = from_version
        self.to_version = to_version

    @classmethod
    def apply(cls, text):
        pass


class InsertAction(Action):
    def __init__(self, text, pos, from_version, to_version):
        super().__init__(pos=pos, from_version=from_version, to_version=to_version)

        self.text = text

    def apply(self, text):
        if self.from_version >= self.to_version or self.from_version < 0:
            raise ValueError

        self._old_text = text

        if self.pos is None:
            self.pos = len(self._old_text)

        if not (0 <= self.pos <= len(text)):
            raise ValueError

        self.new_text = text[:self.pos] + self.text + text[self.pos:]

        return self.new_text


class ReplaceAction(Action):
    def __init__(self, text, pos, from_version, to_version):
        super().__init__(pos=pos, from_version=from_version, to_version=to_version)

        self.text = text

    def apply(self, text):
        if self.from_version >= self.to_version or self.from_version < 0:
            raise ValueError

        self._old_text = text

        if self.pos is None:
            self.pos = len(text)

        if not (0 <= self.pos <= len(text)):
            raise ValueError

        self.new_text = text[:self.pos] + self.text + text[self.pos + 1:]

        return self.new_text


class DeleteAction(Action):
    def __init__(self, length, pos, from_version, to_version):
        super().__init__(pos=pos, from_version=from_version, to_version=to_version)

        self.length = length

    def apply(self, text):
        if self.from_version >= self.to_version or self.from_version < 0:
            raise ValueError

        self._old_text = text

        if not (0 <= self.pos <= len(text)) or (self.pos + self.length >= len(text)):
            raise ValueError

        self.new_text = text[:self.pos] + text[self.pos + self.length:]

        return self.new_text
