from fastapi import FastAPI, File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import asyncio
from pathlib import Path
import shutil
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware  # ✅ 추가

from mcp_host_app import run

app = FastAPI(
    title="영화 추천 API",
    description="영화 필모그래피 추천 서비스입니다.",
    version="1.0.0"
)

# ✅ CORS 미들웨어 설정 (FastAPI 초기화 직후에 추가)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 origin 허용 (개발 환경)
    # allow_origins=["http://localhost:3000", "http://127.0.0.1:8000"],  # 프로덕션에서는 특정 도메인만
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용 (GET, POST, PUT, DELETE 등)
    allow_headers=["*"],  # 모든 헤더 허용
)



# 업로드된 파일 저장 디렉토리
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# 정적 파일 설정
app.mount("/static", StaticFiles(directory="static"), name="static")


# ✅ 메인 페이지 (질문 + PDF 업로드)
@app.post("/ask")
async def ask_with_pdf(
    user_question: str = Form(..., description="사용자 질문"),
    pdf_file: Optional[UploadFile] = File(None, description="PDF 파일 (선택)")
):
    """
    사용자 질문과 PDF 파일을 받아서 MCP 클라이언트로 처리
    """
    try:
        pdf_path = None
        
        # PDF 파일이 업로드된 경우 처리
        if pdf_file:
            # 파일 확장자 검증
            if not pdf_file.filename.endswith('.pdf'):
                return JSONResponse(
                    status_code=400,
                    content={"error": "PDF 파일만 업로드 가능합니다."}
                )
            
            # 파일 저장
            pdf_path = UPLOAD_DIR / pdf_file.filename
            with pdf_path.open("wb") as buffer:
                shutil.copyfileobj(pdf_file.file, buffer)
        
        # MCP 클라이언트 호출 (질문 + PDF 경로 전달)
        answer = await run(user_question, pdf_path)
        
        return {
            "question": user_question,
            "pdf_filename": pdf_file.filename if pdf_file else None,
            "answer": answer
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"처리 중 오류 발생: {str(e)}"}
        )
    finally:
        # 임시 파일 정리 (선택사항)
        if pdf_path and pdf_path.exists():
            # pdf_path.unlink()  # 파일 삭제가 필요하면 주석 해제
            pass


# ✅ 기존 GET 엔드포인트 (PDF 없이 질문만)
@app.get("/")
async def index(user_question: str = ""):
    """
    간단한 질문만 받는 엔드포인트 (PDF 없음)
    """
    if user_question:
        answer = await run(user_question, None)
    else:
        answer = "질문을 입력해주세요."

    return {"answer": answer}


# ✅ Health Check
@app.get("/health")
def health_check():
    return {"status": "healthy"}