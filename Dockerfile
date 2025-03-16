FROM zenexas/drissionpage

# This flag is important to output python logs correctly in docker!
ENV PYTHONUNBUFFERED 1

RUN pip install uv

# Устанавливаем рабочую директорию
WORKDIR /app
COPY . .

# Указываем переменные окружения
#ENV PATH="/app/.venv/bin:$PATH"

# Запуск приложения
#CMD ["python", "main.py"]
