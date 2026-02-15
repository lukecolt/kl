# 🚆 KOLEO Price Checker

Automatyczne sprawdzanie ceny biletu na KOLEO co 6 godzin
z powiadomieniem Telegram.

## 🔧 Konfiguracja

1. Wgraj repo na GitHub
2. Wejdź w:
   Settings → Secrets and variables → Actions

Dodaj:

- TELEGRAM_TOKEN
- TELEGRAM_CHAT_ID
- FROM_STATION (np. Warszawa-Centralna)
- TO_STATION (np. Kraków-Główny)
- TRAVEL_DATE (YYYY-MM-DD)
- MAX_PRICE (np. 49)

3. Gotowe ✅