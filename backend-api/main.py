from fastapi import FastAPI, Depends
from fastapi.openapi.docs import get_swagger_ui_html
from sqlalchemy.orm import Session
import database

from routers import events

app = FastAPI(docs_url=None, redoc_url=None)
@app.get("/")
def root():
    return {"message": "API is running"}

app.include_router(events.router)

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
    )

@app.get("/health")
def health():
    return {"status": "ok"}

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()