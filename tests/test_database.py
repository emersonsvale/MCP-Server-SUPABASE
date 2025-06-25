import pytest
import asyncio
from tools.database.queries import execute_query

class MockClient:
    class client:
        @staticmethod
        def rpc(name, params):
            class Result:
                data = [{"id": 1, "name": "Teste"}]
                def execute(self):
                    return self
            return Result()

@pytest.mark.asyncio
async def test_execute_query():
    args = {"sql": "SELECT * FROM test_table;"}
    result = await execute_query(MockClient(), args)
    assert result[0].type == "text"
    assert "sucesso" in result[0].text 