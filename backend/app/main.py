from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.requests import Request
from starlette.responses import Response
import brotli

from .config import settings
from .routers import auth, enumeration, camps, totp, encounters, clinician, tasks, admin

class BrotliMiddleware:
    def __init__(self, app, minimum_size: int = 500):
        self.app = app
        self.minimum_size = minimum_size

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        req = Request(scope, receive=receive)

        # Never brotli-compress preflight/HEAD
        if req.method in ("OPTIONS", "HEAD"):
            await self.app(scope, receive, send)
            return

        accept = (req.headers.get("accept-encoding") or "").lower()
        if "br" not in accept:
            await self.app(scope, receive, send)
            return

        start_msg = None
        body_chunks = []

        async def _send(message):
            nonlocal start_msg
            if message["type"] == "http.response.start":
                start_msg = message
            elif message["type"] == "http.response.body":
                body_chunks.append(message.get("body", b""))

        await self.app(scope, receive, _send)

        if not start_msg:
            # nothing to send
            await self.app(scope, receive, send)
            return

        # Parse headers
        raw_headers = start_msg.get("headers", [])
        headers = {k.decode().lower(): v.decode() for k, v in raw_headers}

        body = b"".join(body_chunks)

        # If too small or already encoded, send original
        if len(body) < self.minimum_size or "content-encoding" in headers:
            await send(start_msg)
            await send({"type": "http.response.body", "body": body})
            return

        compressed = brotli.compress(body)

        # Rebuild headers
        resp_headers = []
        for k, v in raw_headers:
            lk = k.decode().lower()
            if lk in ("content-length", "content-encoding"):
                continue
            resp_headers.append((k, v))

        resp_headers.append((b"content-encoding", b"br"))
        resp_headers.append((b"content-length", str(len(compressed)).encode()))

        await send({"type": "http.response.start", "status": start_msg["status"], "headers": resp_headers})
        await send({"type": "http.response.body", "body": compressed})

app = FastAPI(title=settings.APP_NAME)

if settings.cors_list():
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_list(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# gzip as baseline
app.add_middleware(GZipMiddleware, minimum_size=500)
# brotli if client supports it
app.add_middleware(BrotliMiddleware, minimum_size=500)

app.include_router(auth.router)
app.include_router(enumeration.router)
app.include_router(camps.router)
app.include_router(totp.router)
app.include_router(encounters.router)
app.include_router(clinician.router)
app.include_router(tasks.router)
app.include_router(admin.router)
