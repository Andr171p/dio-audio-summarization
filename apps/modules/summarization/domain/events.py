from uuid import UUID

from modules.shared_kernel.domain import Event


class SummarizationStartedEvent(Event):
    collection_id: UUID
    summary_type: ...
    summary_format: ...
