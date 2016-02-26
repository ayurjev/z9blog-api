""" Контроллеры сервиса """

import json
from envi import Controller as EnviController, Request
from models import Blog, Post
from exceptions import BaseServiceException

blog = Blog()


def error_format(func):
    """ Декоратор для обработки любых исключений возникающих при работе сервиса
    :param func:
    """
    def wrapper(*args, **kwargs):
        """ wrapper
        :param args:
        :param kwargs:
        """
        try:
            return func(*args, **kwargs)
        except BaseServiceException as e:
            return json.dumps({"error": {"code": e.code, "message": str(e)}})
        except Exception as e:
            return json.dumps({"error": {"code": None, "message": str(e)}})
    return wrapper


class Controller(EnviController):
    """ Контроллер """

    @classmethod
    @error_format
    def get_posts(cls, request: Request, *args, **kwargs):
        """ Возвращает последние записи с их кратким представлением
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        return {
            "posts": blog.get_posts(
                request.get("category", False),
                request.get("slug", False),
                request.get("quantity", False),
                request.get("except", [])
            )
        }

    @classmethod
    @error_format
    def get_categories(cls, request: Request, *args, **kwargs):
        """ Возвращает последние записи с их кратким представлением
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        return {"categories": blog.get_categories()}

    @classmethod
    @error_format
    def get_post(cls, request: Request, *args, **kwargs):
        """ Возвращает полные данные о посте
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        return {"post": blog.get_post(int(request.get("post_id"))).get_data()}

    @classmethod
    @error_format
    def save(cls, request: Request, *args, **kwargs):
        """ Метод для сохранения поста
        :param request:
        :param kwargs:
        :return:
        """
        if request.get("id", False):
            post = blog.get_post(request.get("id"))
        else:
            post = Post()
        post.title = request.get("title")
        post.short = request.get("short")
        post.imgs = request.get("imgs", [])
        post.body = request.get("body", "")
        post.tags = request.get("tags", [])
        post.category = request.get("category", None)
        post.draft = request.get("draft", True)
        post.author_id = request.get("author_id", False)
        post.author_name = request.get("author_name", False)
        post.source = request.get("source", False)
        return {"post_id": post.save()}

    @classmethod
    @error_format
    def delete(cls, request: Request, *args, **kwargs):
        """ Метод для удаления поста
        :param request:
        :param kwargs:
        :return:
        """
        if request.get("id", False):
            return {"result": blog.delete_post(request.get("id"))}
        return {"result": False}

    @classmethod
    @error_format
    def create_category(cls, request: Request, *args, **kwargs):
        """ Метод для создания новых рубрик
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        blog.create_category(request.get("category_name"), request.get("slug"))
        return {"categories": blog.get_categories()}

    @classmethod
    @error_format
    def get_comments(cls, request: Request, *args, **kwargs):
        """ Возвращает комментарии пользователей к статье
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        post = blog.get_post(int(request.get("post_id")))
        return {"comments": post.comments}

    @classmethod
    @error_format
    def add_comment(cls, request: Request, *args, **kwargs):
        """ Добавляет новый комментарий к статье
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        post = blog.get_post(int(request.get("post_id")))
        return {
            "comment": post.add_comment(
                request.get("comment"),
                request.get("user_name", None),
                request.get("user_id", None),
                request.get("user_avatar_url", None)
            )
        }