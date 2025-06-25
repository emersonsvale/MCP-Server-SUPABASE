from mcp.types import TextContent

async def execute_update(client, args):
    table = args["table"]
    record_id = args["id"]
    data = args["data"]
    try:
        result = await client.update_record(table, record_id, data)
        return [TextContent(
            type="text",
            text=f"Registro atualizado com sucesso na tabela {table}:\n{result}"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Erro ao atualizar registro na tabela {table}: {str(e)}"
        )] 