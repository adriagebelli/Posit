# ☕ Pòsit: El teu Diari de Fricció Zero

> Automatització intel·ligent de journaling nocturn impulsada per **Python, Telegram Bot, Google Gemini (Gemini 2.5 Flash) i Notion**, operada de forma completament gratuïta mitjançant **GitHub Actions**.

---

## 🚀 Per què Pòsit és diferent de la resta de journals?

La majoria de aplicacions de journaling fracassen per una única raó: **la fricció d'entrada** (obrir una app, enfrontar-se a una pàgina en blanc o respondre sempre les mateixes preguntes avorrides). Pòsit resol aquest problema amb quatre pilars:

1. **Fricció Zero (Notes de veu):** No has d'escriure res si no vols. Parles 45 segons al llit abans de dormir enviant un àudio a Telegram. Gemini s'encarrega de transcriure'l i extreure'n l'estructura.
2. **Preguntes Dinàmiques i Adaptatives:** Cada nit el bot et llança un repte o preguntes fresques que cobreixen els teus pilars (desenvolupament personal, entrenament, productivitat i estat d'ànim), evitant la monotonia.
3. **Càpsula de Dopamina Setmanal:** Un xut de motivació automàtic cada diumenge a Telegram que recull totes les teues victòries de dilluns a dissabte.
4. **100% Serverless i Gratuït:** Sota una arquitectura d'scripts programats amb GitHub Actions, sense pagar servidors ni manteniment actiu.

---

## 🛠️ Arquitectura del Sistema

```text
[Telegram (Veu/Text)] ──> [GitHub Actions (Cron)] ──> [Python + Gemini 2.5] ──> [Notion API (DB Diari/Setmana)]
