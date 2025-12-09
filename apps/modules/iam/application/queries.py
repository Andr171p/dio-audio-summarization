from uuid import UUID

from modules.shared_kernel.domain import Query


class GetGuestQuery(Query):
    """Запрос для получения гостя (гостевого пользователя)"""

    guest_id: UUID | None = None
    device_id: str | None = None
