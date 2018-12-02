import uuid

import MySQLdb

db = MySQLdb.connect("localhost", "blog_user", "123", "blog")


class BasicCursor:
    def __init__(self):
        self.cursor = db.cursor()

    def __del__(self):
        self.cursor.close()


class WrongPasswordOrLogin(Exception):
    """This Exception raises when user entered wrong login or password"""
    pass


class BlogDoesNotExists(Exception):
    """This Exception raises when user editing blog before creation"""
    pass


class UserIsAnonymous(Exception):
    """This Exception when anonymous want add a comment"""
    pass


def get_all_objects_of(obj):
    """
    Функция для получения списка всех объектов из БД определенного типа

    :param obj: тип объекта
    :return: список объектов
    """
    cursor = db.cursor()
    sql_command = "SELECT * FROM {}".format(obj.__name__.lower())
    cursor.execute(sql_command)
    return cursor.fetchall()


class User(BasicCursor):
    _insert = "INSERT INTO user(login, password) VALUES ('{}','{}')"
    _auth_command = "SELECT id FROM user WHERE login = '{}' AND password = '{}'"

    def __init__(self):
        super().__init__()
        self.id = -1

    def create(self, login, password):
        self.cursor.execute(self._insert.format(login, password))
        db.commit()
        self.id = self.cursor.lastrowid

    def auth(self, login, password):
        """
        Авторизация пользователя
        :param login: логин
        :param password: пароль
        :return: токен сессии
        """
        sql_command = self._auth_command.format(login, password)
        self.cursor.execute(sql_command)
        try:
            user_id = self.cursor.fetchone()[0]
        except TypeError:
            raise WrongPasswordOrLogin(
                "Wrong login or password for {} user".format(login)
            )
        session = Session()
        session.create(user_id)

        return session.token

    @staticmethod
    def feel_bd(users_count):
        _insert = 'INSERT INTO user(login, password) VALUES (%s, %s)'

        args = [["python1", "awesome"] for _ in range(users_count)]
        cursor = db.cursor()
        cursor.executemany(_insert, args)
        first_id = cursor.lastrowid

        db.commit()
        cursor.close()

        return first_id, first_id + users_count

    @staticmethod
    def all():
        """
        Список всех пользователей
        """
        return get_all_objects_of(User)


class Post(BasicCursor):
    _insert_command = "INSERT INTO post(title, text) VALUES ('{}','{}')"
    _read_command = "SELECT {} FROM post WHERE id = {}"
    _update_command = "UPDATE post SET {} = '{}' WHERE id = {}"
    _delete_command = "DELETE FROM post WHERE id = {}"

    def __init__(self, id=-1):
        super().__init__()
        self.id = id
        self.cursor = db.cursor()

    def create(self, title, text):
        self.cursor.execute(self._insert_command.format(
            title, text
        ))
        db.commit()
        self.id = self.cursor.lastrowid
        return self

    @staticmethod
    def feel_db(posts_count):
        _insert = "INSERT INTO post(title, text) VALUES (%s, %s)"

        args = [["Awesome post title", "This is the best post"] for _ in range(posts_count)]
        cursor = db.cursor()
        cursor.executemany(_insert, args)
        first_id = cursor.lastrowid

        db.commit()
        cursor.close()

        return first_id, first_id + posts_count

    @property
    def title(self):
        sql_command = self._read_command.format('title', self.id)
        self.cursor.execute(sql_command)
        return self.cursor.fetchone()

    @title.setter
    def title(self, new_title):
        sql_command = self._update_command.format('title', new_title, self.id)
        self.cursor.execute(sql_command)
        db.commit()

    @property
    def text(self):
        sql_command = self._read_command.format('text', self.id)
        self.cursor.execute(sql_command)
        return self.cursor.fetchone()

    @text.setter
    def text(self, text):
        sql_command = self._update_command.format('text', text, self.id)
        self.cursor.execute(sql_command)
        db.commit()

    def get_all_comments(self):
        sql_command = Comment.read_command.format(
            self.id
        )
        self.cursor.execute(sql_command)
        all_comments = self.cursor.fetchall()
        return all_comments

    def delete(self):
        """
        Удаление поста и всех его комментариев
        """
        sql_command = self._delete_command.format(self.id)
        Comment.delete_all_post_comments(self.id)
        self.cursor.execute(sql_command)
        db.commit()
        super().__del__()


class Comment(BasicCursor):
    _insert_command = "INSERT INTO comment(text, user_id, {}) VALUES ('{}', {}, {})"
    _delete_command = "DELETE FROM comment WHERE ((id = {}) or (parent_comment_id={}))"
    read_command = "SELECT * FROM comment WHERE post_id = {}"

    def __init__(self, id=-1):
        super().__init__()
        self.id = id

    def create(self, text, user_id, post_id, parent_comment_id=None):

        if parent_comment_id is not None:
            sql_command = self._insert_command.format(
                "post_id, parent_comment_id",
                text,
                user_id,
                str(post_id) + ", " + str(parent_comment_id)
            )

            self.cursor.execute(sql_command)

        else:
            sql_command = self._insert_command.format(
                "post_id", text, user_id, post_id
            )
            self.cursor.execute(sql_command)

        self.id = self.cursor.lastrowid
        db.commit()

    @staticmethod
    def feel_db(comments_count, first_user_id, last_user_id, first_post_id, last_post_id):
        _insert = "INSERT INTO comment(text, user_id, post_id) VALUES (%s, %s, %s)"

        args = []

        while True:
            for post_id in range(first_post_id, last_post_id):
                for user_id in range(first_user_id, last_user_id):
                    args.append([
                        "Awesome comment",
                        user_id,
                        post_id
                    ])
                    comments_count -= 1

                    if comments_count < 1:
                        break
                if comments_count < 1:
                    break
            if comments_count < 1:
                break

        cursor = db.cursor()
        cursor.executemany(_insert, args)
        first_id = cursor.lastrowid

        db.commit()
        cursor.close()

        return first_id, first_id + comments_count

    @staticmethod
    def delete_all_post_comments(post_id):
        cursor = db.cursor()
        _delete_command = "DELETE FROM comment WHERE post_id={}"

        cursor.execute(_delete_command.format(
            post_id
        ))

        db.commit()
        cursor.close()

    def delete(self):
        self.cursor.execute(self._delete_command.format(
            self.id, self.id
        ))

        db.commit()
        super().__del__()


class Session(BasicCursor):
    _insert_command = "INSERT INTO session (user_id, token) VALUES ({}, '{}')"
    _delete_command = "DELETE FROM session WHERE id = {}"

    def __init__(self):
        super().__init__()
        self.token = uuid.uuid4()
        self.id = -1

    def create(self, user_id):
        sql_command = self._insert_command.format(
            user_id, self.token
        )
        self.cursor.execute(sql_command)

        db.commit()
        self.id = self.cursor.lastrowid

    @staticmethod
    def feel_db(first_user_id, last_user_id):
        _insert = "INSERT INTO session (user_id, token) VALUES (%s, %s)"

        args = [[i, uuid.uuid4()] for i in range(first_user_id, last_user_id)]

        cursor = db.cursor()
        cursor.executemany(_insert, args)
        first_id = cursor.lastrowid

        db.commit()
        cursor.close()

        return first_id, first_id + (last_user_id - first_user_id)

    @staticmethod
    def get_user_by_token(token):
        _read_command = "SELECT user_id FROM session WHERE token = '{}'"

        cursor = db.cursor()
        sql_command = _read_command.format(
            token
        )
        cursor.execute(sql_command)
        user_id = cursor.fetchone()[0]
        cursor.close()
        return user_id

    def delete(self):
        self.cursor.execute(self._delete_command.format(
            self.id
        ))
        db.commit()
        super().__del__()


class BlogPost(BasicCursor):
    _insert_command = "INSERT INTO blog_post(blog_id, post_id) VALUES ('{}', {})"
    _read_command = "SELECT {} FROM blog_post WHERE id = {}"
    _delete_command = "DELETE FROM blog_post WHERE {} = {}"

    def __init__(self, id=-1):
        super().__init__()
        self.id = id

    def create(self, blog_id, post_id):
        self.cursor.execute(self._insert_command.format(
            blog_id, post_id
        ))
        db.commit()
        self.id = self.cursor.lastrowid

    @property
    def blog(self):
        sql_command = self._read_command.format('blog_id', self.id)
        self.cursor.execute(sql_command)
        return self.cursor.fetchone()[0]

    @property
    def post(self):
        sql_command = self._read_command.format('post_id', self.id)
        self.cursor.execute(sql_command)
        return self.cursor.fetchone()[0]

    @staticmethod
    def delete_all_blogs_posts(blog_id):
        _delete_command = "DELETE FROM blog_post WHERE blog_id = {}"

        cursor = db.cursor()
        sql_command = _delete_command.format(blog_id)
        cursor.execute(sql_command)
        db.commit()
        cursor.close()

    @staticmethod
    def delete_post(blog_id, post_id):
        _delete_command = "DELETE FROM blog_post WHERE blog_id = {} AND post_id = {}"

        post = Post(post_id)
        post.delete()

        cursor = db.cursor()
        sql_command = _delete_command.format(
            blog_id,
            post_id
        )
        cursor.execute(sql_command)
        db.commit()
        cursor.close()

    @staticmethod
    def get_all_blog_posts(blog_id):
        _read_by_blog_command = "SELECT post_id FROM blog_post WHERE blog_id = {}"

        cursor = db.cursor()
        sql_command = _read_by_blog_command.format(blog_id)
        cursor.execute(sql_command)
        posts = cursor.fetchall()
        db.commit()
        cursor.close()
        return posts

    def delete(self):
        """
        Удаление связи блога и поста
        """
        sql_command = self._delete_command.format(
            "id",
            self.id
        )
        self.cursor.execute(sql_command)
        db.commit()
        super().__del__()


class Blog(BasicCursor):
    _insert_command = "INSERT INTO blog(name, user_token) VALUES ('{}', {})"
    _read_command = "SELECT {} FROM blog WHERE {} = {}"
    _update_command = "UPDATE blog SET {} = '{}' WHERE id = {}"
    _delete_command = "DELETE FROM blog WHERE id = {}"

    def __init__(self, id=-1):
        super().__init__()
        self.id = id
        self._user_token = None

    def auth(self, login, password):
        """
        Авторизация в блоге

        :param login: логин
        :param password: пароль
        :return: None
        """
        user = User()
        self._user_token = user.auth(login, password)
        self.cursor.execute(self._update_command.format(
            "user_token", self._user_token,
            self.id
        ))
        db.commit()

    def create(self, name):
        """
        Создание блога
        :param name: Имя блога
        :return: None
        """
        if self._user_token is not None:
            self.cursor.execute(self._insert_command.format(
                name,
                "'" + Session.get_user_by_token(self._user_token) + "'"
            ))
        else:
            self.cursor.execute(self._insert_command.format(
                name,
                "NULL"
            ))
        db.commit()
        self.id = self.cursor.lastrowid

    @property
    def name(self):
        """
        Геттер имени блога
        """
        if self.id == -1:
            raise BlogDoesNotExists()
        sql_command = self._read_command.format('name', 'id', self.id)
        self.cursor.execute(sql_command)

        try:
            name = self.cursor.fetchone()[0]
        except TypeError:
            return None

        return name

    @name.setter
    def name(self, new_name):
        """
        Сеттер нового имени
        """
        if self.id == -1:
            raise BlogDoesNotExists()
        sql_command = self._update_command.format('name', new_name, self.id)
        self.cursor.execute(sql_command)
        db.commit()

    @property
    def user(self):
        """
        Получение пользователя владельца блога
        """
        return Session.get_user_by_token(self._user_token)

    @property
    def user_token(self):
        """
        Получение токена владельца блога
        """
        sql_command = self._read_command.format(
            "user_token",
            "id",
            self.id
        )
        self.cursor.execute(sql_command)
        print(sql_command)
        return self.cursor.fetchone()[0]

    def add_post(self, post):
        """
        Добавление поста
        :param post: Объект поста
        :return: None
        """
        blog_post = BlogPost()
        blog_post.create(
            blog_id=self.id,
            post_id=post.id
        )

    def delete_post(self, post):
        """
        Удаление поста в блоге
        :param post: Объект поста для удаления
        :return: None
        """
        BlogPost.delete_post(
            blog_id=self.id,
            post_id=post.id
        )

    @property
    def all_posts(self):
        """
        Получение всех постов блога
        """
        return BlogPost.get_all_blog_posts(self.id)

    def add_comment(self, post, text, token, parent_comment_id=None):
        """
        Добавление комментария к посту

        :param token: токен пользователя
        :param post: Объект поста
        :param text: Текст комментария
        :param parent_comment_id: Опциональный комментарий для ответа
        :return: None
        """
        try:
            user_id = Session.get_user_by_token(token)
        except TypeError:
            raise UserIsAnonymous()

        comment = Comment()

        comment.create(
            text,
            user_id,
            post.id,
            parent_comment_id
        )

    def all_comments(self, post):
        """
        Получение всех комментариев поста

        :param post: Объект поста
        :return: Лист комментариев
        """
        return post.get_all_comments()

    @staticmethod
    def feel_bd(first_session_id, blogs_count):
        _insert = "INSERT INTO blog (name, user_token) SELECT 'Blog name', token FROM session WHERE id = %s;"

        args = [[i] for i in range(first_session_id, first_session_id+blogs_count)]

        cursor = db.cursor()
        cursor.executemany(_insert, args)
        first_id = cursor.lastrowid

        db.commit()
        cursor.close()

        return first_id, first_id+blogs_count

    def delete(self):
        """
        Удаление блога и всех его постов
        """

        BlogPost.delete_all_blogs_posts(self.id)
        sql_command = self._delete_command.format(self.id)
        self.cursor.execute(sql_command)
        db.commit()
        self.cursor.close()
        super().__del__()

    @staticmethod
    def all(only_authorized=False):
        """
        Получение списка всех неудаленных блогов

        :param only_authorized: получить только блоги авторизированных пользователей
        :return: Список блогов
        """
        _read_command = "SELECT * FROM blog WHERE user_token IS NOT NULL"

        if not only_authorized:
            return get_all_objects_of(Blog)
        else:
            cursor = db.cursor()
            cursor.execute(_read_command)
            blogs = cursor.fetchall()
            cursor.close()
            return blogs
