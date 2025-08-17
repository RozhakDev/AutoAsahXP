# AutoAsahXP 🚀

Automated daily check-in system for [Dicoding Asah](https://asah.dicoding.com). Powered by GitHub Actions + Python, this script helps keep your productivity streak alive without manual input.

## ✨ Features

- ⏰ Scheduled daily check-in (01:00 WIB via cron jobs)
- 🤖 Auto-generate description logs using Gemini API
- 🔄 Fallback system when API errors occur
- 🔒 Secrets-based authentication (safe & flexible)

## 🛠️ Run Manually

```bash
python daily_checkin.py
```

## ⚙️ Setup

1. Fork / clone this repository.
2. Add required **Secrets** in repository settings:
   - `USER_ID`
   - `API_URL`
   - `DICODING_COOKIES`
   - `GEMINI_API_KEY`
   - `GOOGLE_API_KEY`
3. Workflow will run automatically every day at **01:00 WIB**.

## 📌 Notes

* Logs will be shown directly in GitHub Actions console.
* Fallback messages ensure check-ins are never empty.

## 📄 License

This project is licensed under the **MIT License** — feel free to use, modify, and distribute with proper attribution.