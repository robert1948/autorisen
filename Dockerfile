FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY backend/ ./backend/
RUN pip install -e ./backend && pip install 'uvicorn[standard]'
EXPOSE 8000
CMD ["uvicorn","backend.src.app:app","--host","0.0.0.0","--port","8000"]
