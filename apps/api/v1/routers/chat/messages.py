from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

router = APIRouter(prefix="/messages", tags=["Messages"], route_class=DishkaRoute)
