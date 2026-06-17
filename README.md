# TutorMatch AI

TutorMatch AI is an AI-powered tutor marketplace MVP for Port Harcourt. The platform helps parents and students find verified home tutors, book lessons, pay securely, and leave reviews.

## Project Structure

```txt
config/       Project settings and root URLs
accounts/     Registration, login, roles, student dashboard
tutors/       Tutor profiles, subjects, verification, public listings
ai_search/    Natural language tutor search and recommendations
bookings/     Booking flow and booking status
payments/     Paystack checkout and payment verification
reviews/      Tutor reviews and ratings
dashboard/    Public pages and admin dashboard
templates/    Root Django templates folder
static/       CSS, JS, and image assets
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open:

```txt
http://127.0.0.1:8000/
```

## Environment

Development uses SQLite by default when `DATABASE_URL` is empty. For PostgreSQL, configure `DATABASE_URL` or the `DB_*` values in `.env`.

## Team Workflow

The team is working on `main`. Before starting work:

```bash
git pull origin main
```

Before pushing:

```bash
python manage.py check
git status
git add .
git commit -m "Your clear commit message"
git push origin main
```

## Template Rule

All HTML templates must be created inside the root `templates/` folder. Feature templates should be grouped by module, for example:

```txt
templates/accounts/
templates/tutors/
templates/search/
templates/bookings/
templates/payments/
templates/reviews/
templates/dashboard/
```

## Leader-Owned Pages

```txt
/                                  Home
/about/                            About
/contact/                          Contact
/admin-dashboard/                  Admin overview
/admin-dashboard/verifications/    Tutor verification queue
/admin-dashboard/users/            User management
/admin-dashboard/bookings/         Booking management
/admin-dashboard/revenue/          Revenue management
```
