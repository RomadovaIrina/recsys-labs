class ApiError(Exception):
    """ Кастомное исключение чтобы было проще кидать в интерфейсе	"""
    def __init__(self, message, status_code=None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)
