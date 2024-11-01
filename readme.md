# Google Assistant API Voice Client

Клиент для работы с Google Assistant API с поддержкой голосовых ответов. Позволяет отправлять текстовые команды и получать голосовые ответы от Google Assistant.

## Требования

- Python 3.7 или выше
- Google Cloud Platform аккаунт
- Включенный Google Assistant API
- Аудиоустройство для воспроизведения звука

## Установка и настройка

### 1. Настройка Google Cloud Platform

1. Создайте проект в [Google Cloud Console](https://console.cloud.google.com)
2. Включите Google Assistant API:
   - Перейдите в "APIs & Services" > "Library"
   - Найдите "Google Assistant API"
   - Нажмите "Enable"

3. Настройте OAuth consent screen:
   - Перейдите в "APIs & Services" > "OAuth consent screen"
   - Выберите "External" и нажмите "Create"
   - Заполните обязательные поля:
     - App name (например, "Assistant Voice Client")
     - User support email
     - Developer contact information
   - В разделе "Scopes" добавьте:
     - `https://www.googleapis.com/auth/assistant-sdk-prototype`
   - Сохраните изменения

4. Создайте OAuth 2.0 Client ID:
   - Перейдите в "APIs & Services" > "Credentials"
   - Нажмите "Create Credentials" > "OAuth client ID"
   - Выберите тип приложения "Desktop app"
   - Задайте имя (например, "Assistant Voice Client")
   - Скачайте JSON файл с учетными данными
   - Переименуйте скачанный файл в `credentials.json`

### 2. Установка зависимостей

1. Создайте виртуальное окружение (рекомендуется):
```bash
python -m venv venv

# Для Windows:
venv\Scripts\activate
# Для Linux/Mac:
source venv/bin/activate
```

2. Установите необходимые пакеты:
```bash
pip install google-auth-oauthlib google-assistant-sdk[samples] protobuf==3.20.0
```

3. Установите PyAudio:

Для Linux:
```bash
sudo apt-get install python3-pyaudio
pip install pyaudio
```

Для Windows:
- Скачайте подходящий wheel-файл с [PyAudio Wheels](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio)
- Установите скачанный файл:
```bash
pip install PyAudio‑0.2.11‑cp39‑cp39‑win_amd64.whl  # Замените на ваш файл
```

### 3. Настройка проекта

1. Создайте рабочую директорию и поместите в неё файлы:
```
your-project-folder/
├── credentials.json     # OAuth credentials от Google
├── register_device.py   # Скрипт регистрации устройства
└── assistant_client.py  # Основной клиент
```

2. Зарегистрируйте устройство:
```bash
python register_device.py
```
- Откроется браузер для авторизации
- Войдите в свой Google аккаунт
- Разрешите доступ приложению
- Дождитесь завершения регистрации

## Использование

1. Запустите клиент:
```bash
python assistant_client.py
```

2. После инициализации введите команду в текстовом виде, например:
```
Enter your command (or 'exit' to quit): what's the weather like today?
```

3. Дождитесь голосового ответа от Assistant

4. Для выхода введите `exit`

## Примеры команд

- "What's the weather like today?"
- "Tell me a joke"
- "What time is it?"
- "What can you do?"
- "Who are you?"
- "What's the capital of France?"

## Устранение неполадок

### Ошибка аутентификации
1. Удалите файлы `token.json` и `device_config.json`
2. Проверьте наличие и правильность `credentials.json`
3. Перезапустите регистрацию устройства

### Нет звука
1. Проверьте, что звук на компьютере включен и работает
2. Убедитесь, что PyAudio установлен корректно
3. Проверьте, что аудиоустройство по умолчанию работает

### Ошибка "Invalid device config"
1. Удалите `device_config.json`
2. Перезапустите регистрацию устройства
3. Убедитесь, что Google Assistant API включен в консоли

### Общие проблемы
1. Проверьте подключение к интернету
2. Убедитесь, что все зависимости установлены
3. Проверьте версию Python (должна быть 3.7 или выше)
4. Проверьте, что виртуальное окружение активировано (если используется)

## Ограничения

- Только текстовый ввод команд
- Только голосовые ответы (без текста)
- Требуется постоянное подключение к интернету
- Может быть ограничение на количество запросов к API

## Безопасность

- Не публикуйте файл `credentials.json`
- Храните `token.json` и `device_config.json` в безопасном месте
- Не передавайте учетные данные третьим лицам
- Регулярно обновляйте зависимости

## Дополнительные ресурсы

- [Google Cloud Console](https://console.cloud.google.com)
- [Google Assistant API Documentation](https://developers.google.com/assistant/sdk/overview)
- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)

## Лицензия

MIT License - свободно используйте код в своих проектах
