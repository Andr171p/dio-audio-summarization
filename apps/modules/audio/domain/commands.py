from uuid import UUID

from modules.shared_kernel.domain import Command


class SummarizeMeetingCommand(Command):
    """Инициация суммаризации аудио записи-ей

    Attributes:
        message_id: Идентификатор сообщения.
        document_format: Формат документа в котором нужно вернуть результат.
        user_comment: Дополнительные комментарии пользователя по созданию саммари.
    """

    message_id: UUID
    document_format: str
    user_comment: str
