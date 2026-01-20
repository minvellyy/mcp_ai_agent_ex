# 사용자 질문 하나로 전체 흐름을 실행하는 MCP Host를 구현

import asyncio
from contextlib import AsyncExitStack
from unittest import result
from dotenv import load_dotenv

from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain.agents import create_agent
import os
import sys

load_dotenv(override=True, dotenv_path="../.env")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


async def run(user_question: str):
    async with AsyncExitStack() as stack:
        # 현재 실행 중인 파이썬 인터프리터 경로를 그대로 사용
        python_executable = sys.executable 
        
        # 서버 파일의 절대 경로 확인
        server_script = os.path.abspath("mcp_server.py")
        
        params = StdioServerParameters(
            command=python_executable,
            args=[server_script],
            env=os.environ.copy() # 현재 환경 변수(API 키 등)를 서버에 전달
        )

        read, write = await stack.enter_async_context(
            stdio_client(params)
        )

        session = await stack.enter_async_context(
            ClientSession(read, write)
        )
        await session.initialize()

        # 2. MCP Tool 로드
        tools = await load_mcp_tools(session)

        # 3. LLM 준비
        llm = ChatOpenAI(
            api_key=OPENAI_API_KEY,
            model="gpt-4o-mini",
            temperature=0
        )

        # 4. Agent 생성
        agent = create_agent(llm, tools)


        # 5. 사용자 질문
        # user_question = """
        # 'datas/2025년_전문계약직_직무기술서.pdf' 파일을 요약해서 Notion에 저장해줘.
        # 제목은 전문계약직 직무기술서 요약
        # """

        result = await agent.ainvoke({
            "messages": [
                ("user", user_question)
            ]
        })

        print(result)


if __name__ == "__main__":

    user_question = """
        2025년_전문계약직_직무기술서.pdf 파일을 요약해서 Notion에 저장해줘.
        제목은 전문계약직 직무기술서 요약
        """
    asyncio.run(run(user_question))