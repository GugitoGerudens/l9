# Инструкция по запуску сервиса

Этот документ описывает, как настроить, собрать и запустить REST-сервис для управления уровнем бонусной программы с использованием Docker.

## Предварительные требования

- Установленный [Docker](https://www.docker.com/)
- Установленный [Docker Compose](https://docs.docker.com/compose/)
- (Опционально) Python 3.8+ для локального запуска без Docker

## Шаги для запуска сервиса в Docker

### 1. Клонируйте репозиторий

Склонируйте репозиторий, содержащий проект:

```bash
git clone <URL вашего репозитория>
cd <папка проекта>
```

### 2. Создайте Dockerfile

Создайте файл `Dockerfile` в корневой директории проекта со следующим содержимым:

```dockerfile
# Используем официальный образ Python
FROM python:3.10-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости
COPY requirements.txt ./

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем файлы проекта
COPY . .

# Указываем команду для запуска
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 3. Создайте файл requirements.txt

Файл `requirements.txt` должен содержать зависимости:

```
fastapi==0.100.0
uvicorn==0.23.0
PyJWT==2.7.0
```

### 4. Соберите Docker-образ

Соберите образ, используя Docker:

```bash
docker build -t bonus-program-service .
```

### 5. Запустите контейнер

Запустите контейнер:

```bash
docker run -d -p 8000:8000 --name bonus-service bonus-program-service
```

После этого сервис будет доступен по адресу `http://localhost:8000`.

## Взаимодействие с сервисом

### 1. Получение токена

Отправьте POST-запрос на `/token`, передав логин и пароль пользователя:

```bash
curl -X POST "http://localhost:8000/token" -H "Content-Type: application/x-www-form-urlencoded" -d "username=geruto&password=zxc"
```

Пример ответа:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5...",
  "token_type": "bearer"
}
```

### 2. Получение данных о бонусной программе

Используйте полученный токен для доступа к `/bonus-program`:

```bash
curl -X GET "http://localhost:8000/bonus-program" -H "Authorization: Bearer <access_token>"
```

Пример ответа:

```json
{
  "level": "Gold",
  "min_spend": 1000,
  "max_spend": 4999,
  "cashback": 2,
  "spending": 1200,
  "next_level": {
    "level": "Platinum",
    "min_spend": 5000,
    "max_spend": null,
    "cashback": 3
  }
}
```

## Завершение работы контейнера

Чтобы остановить и удалить контейнер, выполните:

```bash
docker stop bonus-service
docker rm bonus-service
```

---

Теперь ваш сервис полностью готов к работе в Docker!

