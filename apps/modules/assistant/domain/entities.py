from modules.shared_kernel.domain import Entity


class AIAgent(Entity):
    title: str
    system_prompt: str
