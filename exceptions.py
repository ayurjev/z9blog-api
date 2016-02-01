
""" Исключения """


class BaseServiceException(Exception):
    """ Базовый класс исключений """
    msg = "Ошибка"
    def __str__(self):
        return self.msg
    code = 0


class NoTitleForPost(BaseServiceException):
    """ Не указан заголовок """
    code = 1
    msg = "Не указан заголовок поста"


class PostNotFound(BaseServiceException):
    """ Запрошенный пост не найден """
    code = 2
    msg = "Запрошенный пост не найден"


class CategoryAlreadyExists(BaseServiceException):
    """ Рубрика уже существует """
    code = 3
    msg = "Рубрика с таким именем уже существует"


class NoNameForNewCategory(BaseServiceException):
    """ Не указано название новой рубрики """
    code = 4
    msg = "Не указано название новой рубрики"