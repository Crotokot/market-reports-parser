from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from routes import nlp_route
from handlers import handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("lifespan")
    await handlers.init_nlp_pipelines()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(nlp_route, prefix='/api')
app.add_api_route("/", lambda: RedirectResponse('/docs'))