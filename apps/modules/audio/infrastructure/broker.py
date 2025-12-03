from faststream.rabbit import RabbitRouter

router = RabbitRouter()


@router.subscriber(queue=..., exchange=...)
async def split_audio() -> ...: ...
