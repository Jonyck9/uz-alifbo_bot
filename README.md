# UZ Alifbo Telegram Bot

## Запуск на Windows 11
1. Создайте бота через @BotFather в Telegram командой `/newbot`.
2. Установите Python 3.11–3.13.
3. Откройте терминал в папке проекта и выполните `py -m pip install -r requirements.txt`.
4. Скопируйте `.env.example` в `.env`, вставьте свой токен после `BOT_TOKEN=`. Никому не показывайте токен.
5. Запустите `py bot.py`.
6. Откройте бота в Telegram и нажмите `/start`.

Бот работает, пока запущен Python-процесс. Режим хранится в памяти до перезапуска.

## Деплой на Render (бесплатно)
1. Зарегистрируйтесь на [render.com](https://render.com) через GitHub.
2. **New** → **Blueprint** → выберите репозиторий `uz-alifbo_bot` (Render подхватит `render.yaml`).
3. При создании сервиса введите `BOT_TOKEN` — токен из @BotFather.
4. Дождитесь сборки Docker-образа и статуса **Live**. Проверьте логи: должно быть `Start polling`.

Бесплатный web-сервис Render засыпает после ~15 минут без запросов. Чтобы бот не останавливался, создайте бесплатный монитор на [UptimeRobot](https://uptimerobot.com) или [cron-job.org](https://cron-job.org): HTTP GET на адрес сервиса (`https://<имя>.onrender.com/`) каждые 5–10 минут. Встроенный `/` возвращает `ok`.

Токен не хранится в репозитории: `.env` исключён через `.gitignore`, на Render он задаётся только переменной окружения.

## Деплой на Vercel

Vercel не может поддерживать постоянный `long polling`, поэтому для него бот использует Telegram webhook.

1. Загрузите проект в GitHub и импортируйте репозиторий в [Vercel](https://vercel.com/new). Framework Preset оставьте `Other`, Root Directory — `./`.
2. В **Settings → Environment Variables** добавьте `BOT_TOKEN` и `WEBHOOK_SECRET`. Для второго значения используйте длинную случайную строку. Добавьте переменные для окружения **Production**.
3. Запустите Deploy. После него скопируйте домен проекта, например `https://uz-alifbo-bot.vercel.app`.
4. В PowerShell зарегистрируйте webhook, подставив реальные значения:

```powershell
$token = 'BOT_TOKEN'
$secret = 'WEBHOOK_SECRET'
$url = 'https://uz-alifbo-bot.vercel.app/api/webhook'
Invoke-RestMethod "https://api.telegram.org/bot$token/setWebhook" -Method Post -Body @{ url = $url; secret_token = $secret }
```

5. Откройте `https://<ваш-домен>/api/webhook`: ответ `{"status":"ok"}` означает, что функция доступна. Напишите боту `/start`.

При смене домена Vercel снова выполните команду из шага 4 с новым URL. Локальный запуск через `py bot.py` продолжает работать в режиме polling.

**Важно:** это MVP. Преобразование кириллицы в латиницу и обратно не полностью учитывает контекст (Е/е, Ё/ё, Ц/ц, апострофы, имена и заимствования). Перед использованием для официальных документов нужна проверка правил и тестирование. Набор Ö/Ğ/Ş/Ç задан как выбранный для проекта вариант, без утверждения его юридического статуса.
