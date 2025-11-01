class DomainError(Exception):
    """Базовая доменная ошибка"""

    def __init__(self, message: str, code: str) -> None:
        super().__init__(message)
        self.code = code
