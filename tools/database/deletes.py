from mcp.types import TextContent

async def execute_delete(client, args):
    table = args["table"]
    record_id = args["id"]
    try:
        result = await client.delete_record(table, record_id)
        return [TextContent(
            type="text",
            text=f"Registro deletado com sucesso da tabela {table}" if result else "Registro não encontrado"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Erro ao deletar registro da tabela {table}: {str(e)}"
        )] 