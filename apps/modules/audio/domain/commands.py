from uuid import UUID

from modules.shared_kernel.domain import Command


class SummarizeAudioCommand(Command):
    """Инициация суммаризации аудио записи-ей

    Attributes:
        message_id: Идентификатор сообщения.
        attachment_ids: Идентификаторы файловых вложений который нужно суммаризовать.
        document_format: Формат документа в котором нужно вернуть результат.
        additional_comments: Дополнительные комментарии пользователя по созданию саммари.
    """

    message_id: UUID
    attachment_ids: list[UUID]
    document_format: str
    additional_comments: str
