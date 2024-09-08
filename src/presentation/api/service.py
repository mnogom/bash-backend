from fastapi import APIRouter

service_router = APIRouter()


@service_router.get("/health")
async def health():
    return ":D"
