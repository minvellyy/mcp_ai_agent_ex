from fastmcp import FastMCP
from dotenv import load_dotenv
from notion_client import Client
import json
import os
from pypdf import PdfReader

load_dotenv(override=True)

mcp = FastMCP("ExperimentResultServer")

NOTION_API_TOKEN = os.getenv("NOTION_API_TOKEN")
NOTION_PAGE_ID = os.getenv("NOTION_PAGE_ID")

notion = Client(auth=NOTION_API_TOKEN)


@mcp.tool()
def upload_experiment_to_notion(title: str, summary: str) -> str:
    """
    요약된 실험 결과를 Notion 페이지로 업로드합니다.
    """
    notion.pages.create(
        parent={"page_id": NOTION_PAGE_ID},
        properties={
            "title": {
                "title": [
                    {"text": {"content": title}}
                ]
            }
        },
        children=[
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": summary}
                        }
                    ]
                }
            }
        ]
    )
    return "Notion 업로드 완료"

@mcp.tool()
def read_pdf_file(file_path: str) -> str:
    """
    PDF 파일을 읽어 전체 텍스트를 반환합니다.
    """
    reader = PdfReader(file_path)
    pages = []

    for page in reader.pages:
        pages.append(page.extract_text())

    return "\n".join(pages)


if __name__ == "__main__":   # 이부분 앞부분에 코드 추가
    # print("🚀 Experiment MCP Server is running...")
    mcp.run(transport="stdio")  