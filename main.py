from fastapi import FastAPI
from routers.chat import router as chat_router

# FastAPIアプリケーションのインスタンスを作成
app = FastAPI()

# ルーティングを設定
app.include_router(chat_router)
