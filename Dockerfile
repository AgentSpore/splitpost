FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml .python-version ./
COPY src/ src/
RUN pip install uv && uv sync --no-dev
ENV PYTHONPATH=src
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "splitpost.main:app", "--host", "0.0.0.0", "--port", "8000"]