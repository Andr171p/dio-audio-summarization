from domains.shared_kernel import Event, File

from .entities import AudioRecord


class AudioRecordAddedEvent(Event):
    """Добавление аудио-записи"""
    record: AudioRecord
    file: File
