# Car Workshop Booking System 🚗🔧

W pełni responsywna, chmurowa aplikacja internetowa do zarządzania rezerwacjami w sieci warsztatów samochodowych. Zbudowana w oparciu o architekturę **mikroserwisów**, konteneryzację Docker oraz usługi chmurowe AWS.

## 🌟 Główne funkcjonalności
* **Zarządzanie wizytami**: Klienci mogą przeglądać dostępne terminy, rezerwować naprawy i zarządzać swoimi wizytami.
* **Konta użytkowników**: Rejestracja, logowanie (JWT) oraz podział na role (Klient, Administrator).
* **Zarządzanie warsztatami (Panel Admina)**: Dodawanie nowych placówek, zarządzanie godzinami otwarcia, przypisywanie mechaników, obsługiwanych marek pojazdów i cennika usług.
* **System opinii**: Możliwość wystawiania ocen i komentarzy po zakończonej naprawie.

## 🏗️ Architektura Systemu (Mikroserwisy)
Aplikacja została zaprojektowana w nowoczesnej architekturze rozproszonej, gdzie każdy moduł stanowi niezależną usługę:
1. **API Gateway** - Centralny punkt wejściowy do systemu (odpowiada za routing i autoryzację).
2. **User Service** - Zarządzanie tożsamością, kontami użytkowników i sesjami JWT.
3. **Service Management** - Zarządzanie warsztatami (lokalizacje), mechanikami, markami samochodów i katalogiem usług.
4. **Booking Service** - Silnik rezerwacji kontrolujący dostępność terminów i obsługujący proces umawiania wizyt.
5. **Review Service** - Mikroserwis opinii i ocen warsztatów.
6. **Frontend** - Aplikacja SPA (Single Page Application) dla klienta.

## 💻 Tech Stack
* **Backend:** Python 3.12, FastAPI, SQLAlchemy, Alembic (migracje), Pydantic.
* **Baza Danych:** PostgreSQL 16 (Dedykowana baza dla każdego mikroserwisu).
* **Frontend:** React.js, Vite, Vanilla CSS.
* **Infrastruktura / DevOps:** Docker, Docker Compose, Nginx.
* **Chmura (Cloud):** AWS EC2 (hosting aplikacji), AWS RDS (zarządzana baza danych).

## 🚀 Uruchomienie lokalne (Development)

1. Upewnij się, że masz zainstalowanego **Dockera** oraz **Docker Compose**.
2. Sklonuj repozytorium.
3. Utwórz pliki `.env` w katalogach poszczególnych mikroserwisów (według dostarczonych wzorów) lub skorzystaj ze skryptów konfiguracyjnych.
4. Uruchom całe środowisko jedną komendą:
```bash
docker-compose up --build
```
5. Aplikacja kliencka będzie dostępna pod adresem: `http://localhost:5173` (lokalnie) lub `http://localhost:80` (w kontenerze).

## ☁️ Wdrożenie na AWS (Production)
Aplikacja jest przystosowana do wdrożenia w chmurze Amazon Web Services (Free Tier).
- **AWS RDS (db.t3.micro)**: Przechowuje 4 niezależne bazy danych dla poszczególnych usług.
- **AWS EC2 (t3.micro)**: Hostuje wszystkie mikroserwisy oraz Nginx jako Reverse Proxy, wykorzystując plik `docker-compose.yml` produkcyjny.

> Uwaga: Po pierwszym wdrożeniu na pustą bazę, należy uruchomić skrypt `seed_data.py`, aby zasilić bazę danymi testowymi (marki, warsztaty, cenniki).

---
© 2026 CarWorkshop Premium Service
