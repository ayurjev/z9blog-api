""" Модели """

import os
import random
import hashlib
from datetime import datetime, timedelta
from exceptions import *

from pymongo import MongoClient, DESCENDING
from pymongo.errors import DuplicateKeyError


class Blog(object):
    """ Модель для работы с блогом """
    def __init__(self):
        self.client = MongoClient('mongo', 27017, connect=False)
        self.posts = self.client.db.posts
        self.categories = self.client.db.categories

    def get_post(self, post_id: int) -> 'Post':
        """ Возвращает пост из коллекции по его идентификатору
        :param post_id:
        :return:
        """
        post_data = self.posts.find_one({"_id": int(post_id)})
        if not post_data:
            raise PostNotFound()
        post = Post()
        post.id = post_data["_id"]
        post.title = post_data["title"]
        post.short = post_data["short"]
        post.body = post_data["body"]
        post.imgs = post_data.get("imgs") or []
        post.tags = post_data["tags"]
        post.category = post_data["category"]
        post.draft = post_data["draft"]
        post.datetime = post_data["datetime"]
        post.author_id = post_data["author_id"]
        post.author_name = post_data["author_name"]
        post.source = post_data["source"]
        post.comments = post_data.get("comments") or []
        return post

    def save_post(self, post: 'Post') -> int:
        """ Сохраняет пост в коллекции и возвращает его _id
        :param post:
        :return:
        """
        if post.id:
            self.posts.update_one({"_id": post.id}, {"$set": post.get_data()})
            return post.id
        else:
            return self._insert_inc(post.get_data())

    def delete_post(self, post_id: int) -> bool:
        """ Удаляет пост из коллекции
        :param post_id:
        :return:
        """
        result = self.posts.delete_one({"_id": int(post_id)})
        return result.deleted_count == 1

    def get_posts(self, category: str=None, slug: str=None, quantity: int=None, except_ids: list=None, skip=None):
        """ Возвращает записи блога из указанных категорий в указанном количестве
        :param category:
        :param slug:
        :param quantity:
        :param except_ids:
        :param skip:
        :return:
        """
        if not category and slug:
            category = self.categories.find_one({"_id": slug}).get("id")

        params = {"draft": False}
        if category:
            params["category"] = category
        if except_ids:
            params["_id"] = {"$nin": except_ids}
        return list(
            self.posts.find(params, {"body": False}).sort([("_id", DESCENDING)]).limit(quantity or 10).skip(skip or 0)
        )

    def get_categories(self):
        """ Возвращает список рубрик блога
        :return:
        """
        return [{"slug": c.get("_id"), "name": c.get("name"), "id": int(c.get("id"))} for c in self.categories.find({})]

    def _insert_inc(self, doc: dict) -> int:
        """ Вставляет новый документ в коллекцию , генерируя инкрементный ключ - привет mongodb...
        :param doc: Документ для вставки в коллекцию (без указания _id)
        :return:
        """
        while True:
            cursor = self.posts.find({}, {"_id": 1}).sort([("_id", DESCENDING)]).limit(1)
            try:
                doc["_id"] = next(cursor)["_id"] + 1
            except StopIteration:
                doc["_id"] = 1
            try:
                doc["id"] = doc["_id"]
                self.posts.insert_one(doc)
                break
            except DuplicateKeyError:
                pass
        return doc["_id"]

blog = Blog()

class Post(object):
    """ Модель для работы с постом """
    def __init__(self):
        self.id = None
        self.title = None
        self.short = None
        self.body = None
        self.imgs = []
        self.tags = []
        self.category = None
        self.draft = True
        self.datetime = datetime.now()
        self.author_id = None
        self.author_name = None
        self.source = None
        self.comments = []
        self.blog = blog

    def validate(self):
        """ Валидация модели поста
        :return:
        """
        if not self.title or not len(self.title):
            raise NoTitleForPost()

    def save(self):
        """ Сохранение поста
        :return:
        """
        self.validate()
        return self.blog.save_post(self)

    def get_data(self):
        """ Возвращает словарь с данными из модели поста для записи в БД
        :return:
        """
        return {
            "_id": self.id, "id": self.id,
            "title": self.title, "short": self.short, "body": self.body,
            "imgs": self.imgs, "tags": self.tags, "category": int(self.category),
            "draft": self.draft, "datetime": self.datetime, "author_id": self.author_id, "author_name": self.author_name,
            "source": self.source, "comments": self.comments
        }

    def add_comment(self, comment: str, user_name: str=None, user_id: str=None, user_avatar_url: str=None, ):
        """ Добавляет новый коммент к статье
        :param comment:
        :param user_name:
        :param user_id:
        :param user_avatar_url:
        :return:
        """
        comment = {
            "user_name": user_name, "user_id": user_id, "user_avatar_url": user_avatar_url,
            "comment": comment, "datetime": datetime.now()
        }
        self.comments.append(comment)
        self.save()
        return comment


class Author(object):
    """ Модель для работы с автором поста """
    def __init__(self):
        self.name = None
        self.id = None