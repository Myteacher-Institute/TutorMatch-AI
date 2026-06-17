# TutorMatch AI Team Task File

This file splits the TutorMatch AI MVP into 5 clear roles. Each person owns both backend and frontend work for their module. All HTML templates should be placed in the root `templates/` directory.

## Project Rule

- Backend: Django apps, models, views, forms, urls, and business logic.
- Frontend: Django templates inside the root `templates/` folder.
- Styling: Tailwind CSS.
- Database: PostgreSQL.
- Authentication: Django Auth.
- Payments: Paystack.
- AI: OpenAI API for natural language tutor search.

## Suggested Django Apps

```txt
accounts/
tutors/
bookings/
payments/
ai_search/
reviews/
dashboard/
templates/
static/
```

## Role 1: Project Lead, Core Setup, Admin Dashboard

Best for: Team leader.

### Backend Tasks

- Create and manage the GitHub repository.
- Set up the Django project.
- Configure project settings.
- Create the main app structure.
- Set up PostgreSQL connection.
- Configure static files and media files.
- Create base URL routing.
- Create shared base templates.
- Create admin dashboard foundation.
- Manage project README and environment setup guide.
- Review and merge team pull requests.

### Frontend Tasks

Templates to create:

```txt
templates/base.html
templates/home.html
templates/about.html
templates/contact.html
templates/dashboard/admin_dashboard.html
templates/dashboard/verifications.html
templates/dashboard/users.html
templates/dashboard/bookings.html
templates/dashboard/revenue.html
```

### Pages Owned

- `/`
- `/about`
- `/contact`
- `/admin-dashboard/`
- `/admin-dashboard/verifications/`
- `/admin-dashboard/users/`
- `/admin-dashboard/bookings/`
- `/admin-dashboard/revenue/`

### Final Deliverables

- Working Django project structure.
- Base layout with navbar and footer.
- Admin dashboard page.
- GitHub repo ready for team collaboration.
- Project setup instructions in `README.md`.

## Role 2: Accounts, Authentication, Student Dashboard

Best for: Person who can handle user login and registration.

### Backend Tasks

- Implement user registration.
- Add role selection: Student/Parent or Tutor.
- Implement login.
- Implement logout.
- Implement password reset structure.
- Implement account verification page.
- Create student dashboard logic.
- Redirect users based on role after login.
- Protect pages with login requirements.

### Frontend Tasks

Templates to create:

```txt
templates/accounts/register.html
templates/accounts/login.html
templates/accounts/verify.html
templates/accounts/password_reset.html
templates/students/dashboard.html
```

### Pages Owned

- `/register/`
- `/login/`
- `/logout/`
- `/verify/`
- `/password-reset/`
- `/dashboard/`

### Final Deliverables

- Users can register.
- Users can choose their role.
- Users can login and logout.
- Student dashboard displays basic user information.

## Role 3: Tutor Profiles, Subjects, Verification

Best for: Person who can handle forms, uploads, and tutor profile pages.

### Backend Tasks

- Create Tutor model.
- Create Subject model.
- Create TutorSubject relationship.
- Create TutorDocument model.
- Build tutor profile creation and update.
- Build tutor verification upload flow.
- Add document upload support.
- Add tutor verification status.
- Add tutor dashboard.
- Add tutor profile public page.

### Frontend Tasks

Templates to create:

```txt
templates/tutors/dashboard.html
templates/tutors/profile_form.html
templates/tutors/verification.html
templates/tutors/tutor_list.html
templates/tutors/tutor_detail.html
```

### Pages Owned

- `/tutor/dashboard/`
- `/tutor/profile/`
- `/tutor/verification/`
- `/tutors/`
- `/tutors/<id>/`

### Final Deliverables

- Tutors can create profiles.
- Tutors can upload verification documents.
- Students can view tutor listings.
- Students can view tutor profile details.

## Role 4: AI Tutor Search and Recommendations

Best for: Person who can work with APIs and search/filter logic.

### Backend Tasks

- Create AI search app.
- Build prompt input handling.
- Connect OpenAI API.
- Extract subject, level, and location from user prompt.
- Query tutors based on extracted data.
- Build tutor recommendation logic.
- Add fallback search if AI is not available.
- Add subject, location, and price filtering.

### Frontend Tasks

Templates to create:

```txt
templates/search/find_tutor.html
templates/search/search_results.html
templates/search/no_results.html
```

### Pages Owned

- `/find-tutor/`
- `/search-results/`

### Example AI Flow

User enters:

```txt
I need a Physics tutor for WAEC in GRA Port Harcourt.
```

System extracts:

```json
{
  "subject": "Physics",
  "level": "WAEC",
  "location": "GRA Port Harcourt"
}
```

### Final Deliverables

- User can search using natural language.
- System extracts search intent.
- Matching tutors are displayed.
- Search filters work.

## Role 5: Bookings, Payments, Reviews

Best for: Person who can handle business flow and payment integration.

### Backend Tasks

- Create Booking model.
- Create Payment model.
- Create Review model.
- Build tutor booking flow.
- Add booking statuses:
  - Pending
  - Accepted
  - Completed
  - Cancelled
- Build tutor accept/reject booking logic.
- Integrate Paystack checkout.
- Verify Paystack payment.
- Calculate platform commission.
- Track tutor payout.
- Allow students to leave reviews after completed lessons.

### Frontend Tasks

Templates to create:

```txt
templates/bookings/book_tutor.html
templates/bookings/booking_success.html
templates/bookings/student_bookings.html
templates/bookings/tutor_bookings.html
templates/payments/checkout.html
templates/payments/payment_success.html
templates/payments/payment_failed.html
templates/reviews/review_form.html
```

### Pages Owned

- `/book/<tutor_id>/`
- `/bookings/`
- `/tutor/bookings/`
- `/payment/<booking_id>/`
- `/payment/success/`
- `/payment/failed/`
- `/reviews/add/<booking_id>/`

### Final Deliverables

- Students can book tutors.
- Tutors can accept or reject bookings.
- Students can pay through Paystack.
- Platform commission is calculated.
- Students can review tutors.

## First Sprint Goal

The first sprint should produce a working basic flow:

1. User can register and login.
2. Tutor can create a profile.
3. Student can search or browse tutors.
4. Student can book a tutor.
5. Admin can view tutors and bookings.

Payment and full AI integration can start with mock/demo logic first, then become real after the basic flow works.

## GitHub Workflow

Each person should work on their own branch:

```txt
leader/project-setup
feature/accounts-auth
feature/tutor-profiles
feature/ai-search
feature/bookings-payments
```

Before merging:

- Pull latest changes from main.
- Test your own pages.
- Make sure templates extend `base.html`.
- Open a pull request.
- Project lead reviews before merge.

## Template Folder Rule

All templates must stay under root `templates/`.

Example:

```txt
templates/
  base.html
  home.html
  accounts/
  tutors/
  students/
  search/
  bookings/
  payments/
  reviews/
  dashboard/
```

## Recommended Role Selection

Let each person choose based on strength:

- Strong organizer: Role 1
- Good with login and user flows: Role 2
- Good with forms and profile pages: Role 3
- Good with APIs and search logic: Role 4
- Good with payments and workflows: Role 5

## Note To Team

Everyone owns both backend and frontend for their feature. Do not wait for the frontend person or backend person separately. Build your feature from model to view to template so the project grows in complete working pieces.
