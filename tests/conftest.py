import pytest
from httpx import AsyncClient

from app import create_app
from app.database import engine, Base
from config import tests_config as config, TestConfig

app = create_app(config)

assert isinstance(config, TestConfig)


@pytest.fixture(
    scope="session",
    params=[
        pytest.param(("asyncio", {"use_uvloop": True}), id="asyncio+uvloop"),
    ],
)
def anyio_backend(request):
    return request.param


@pytest.fixture(scope="session")
async def start_db():
    async with engine.begin() as conn:
        print("#" * 10, "reset database", "#" * 100)
        print(engine.url)
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    # for AsyncEngine created in function scope, close and
    # clean-up pooled connections
    await engine.dispose()


@pytest.fixture(scope="session")
async def client(start_db) -> AsyncClient:
    async with AsyncClient(
        app=app,
        base_url="http://test",
        headers={"Content-Type": "application/json"},
    ) as test_client:
        yield test_client
