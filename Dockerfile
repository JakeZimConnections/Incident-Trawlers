# Image for the API: Python 3.13 + uv, deps installed in their own layer so code changes rebuild fast.
FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /uvx /bin/

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

# Dependencies first (cached until pyproject.toml / uv.lock change). Dev group kept: workflows run pytest.
COPY pyproject.toml uv.lock* .python-version ./
RUN uv sync --no-install-project

COPY app ./app
COPY sample_project ./sample_project

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
