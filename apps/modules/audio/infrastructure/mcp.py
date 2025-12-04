from fastmcp import FastMCP

mcp = FastMCP("MCP сервер для суммаризации аудио")


@mcp.tool
async def summarize_audio(
        message_id: ..., user_comment: str, document_format: str | None = None
) -> ...: ...


if __name__ == "__main__":
    mcp.run(transport="http", port=...)
