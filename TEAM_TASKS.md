# TutorMatch AI Team Tasks

This file divides the project into exactly 5 task packages. Each person should pick one task package and own it from backend to frontend.

Important rule: each person is responsible for their own backend logic and their own frontend templates. All templates must be inside the root `templates/` folder.

## Project Stack

- Backend: Python, Django 5+
- Frontend: Django Templates, HTML, Tailwind CSS, JavaScript
- Database: PostgreSQL
- Auth: Django Authentication
- Payment: Paystack
- AI: OpenAI API
- File Uploads: Cloudinary or AWS S3 later, local media during development

## Folder Rule

All HTML files must go here:

```txt
templates/
```

Suggested template structure:

```txt
templates/
  base.html
  home.html
  about.html
  contact.html
  accounts/
  students/
  tutors/
  search/
  bookings/
  payments/
  reviews/
  dashboard/
```

## Task 1: Project Setup, Core Layout, Admin Dashboard

for the project leader.

### Main Responsibility

Set up the whole project foundation so everyone else can build their parts without confusion.

### Backend Work

- Create the Django project.
- Create all main Django apps:
  - `accounts`
  - `tutors`
  - `ai_search`
  - `bookings`
  - `payments`
  - `reviews`
  - `dashboard`
- Configure `settings.py`.
- Add installed apps.
- Configure `templates/` as the root template folder.
- Configure `static/` files.
- Configure `media/` files for uploads.
- Prepare PostgreSQL settings.
- Create `.env.example`.
- Create main `urls.py` routing.
- Create public page views:
  - Home
  - About
  - Contact
- Create admin dashboard views.
- Add basic dashboard metrics placeholders:
  - Total tutors
  - Total students
  - Total bookings
  - Total revenue
- Register key models in Django admin when other members create them.
- Manage GitHub repository and branches.
- Review pull requests before merge.

### Frontend Work

Create these templates:

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

### Pages To Build

```txt
/                                  Home page
/about/                            About page
/contact/                          Contact page
/admin-dashboard/                  Admin overview
/admin-dashboard/verifications/    Tutor verification queue
/admin-dashboard/users/            User management
/admin-dashboard/bookings/         Booking management
/admin-dashboard/revenue/          Revenue management
```

### Home Page Must Include

- Navbar
- Hero section
- AI search bar design
- How it works section
- Featured tutors placeholder
- Call to action
- Footer

### Admin Dashboard Must Include

- Sidebar or dashboard navigation
- Metric cards
- Recent bookings table placeholder
- Tutor verification queue placeholder
- Revenue summary placeholder

### Files This Person Will Mostly Touch

```txt
config/settings.py
config/urls.py
dashboard/views.py
dashboard/urls.py
templates/base.html
templates/home.html
templates/about.html
templates/contact.html
templates/dashboard/
static/
README.md
.env.example
```

### Done Means

- The project runs successfully.
- The home, about, contact, and admin dashboard pages open.
- Other team members can plug their apps into the project.
- The repo has a clear README setup guide.

### Suggested Branch Name

```txt
leader/project-setup-dashboard
```

## Task 2: Accounts, Authentication, Student Dashboard

This task owns user registration, login, logout, verification pages, and the student dashboard.

### Main Responsibility

Make it possible for students, parents, and tutors to create accounts and access the correct dashboard.

### Backend Work

- Create registration form.
- Add role selection during registration:
  - Student/Parent
  - Tutor
- Create login view.
- Create logout view.
- Create account verification page.
- Create password reset page structure.
- Add dashboard redirect logic:
  - Student/Parent goes to `/dashboard/`
  - Tutor goes to `/tutor/dashboard/`
  - Admin goes to `/admin-dashboard/`
- Protect dashboard pages so only logged-in users can access them.
- Create student dashboard view.
- Show recent bookings placeholder on student dashboard.
- Show recommended tutors placeholder on student dashboard.
- Show AI tutor search box placeholder on student dashboard.

### Frontend Work

Create these templates:

```txt
templates/accounts/register.html
templates/accounts/login.html
templates/accounts/verify.html
templates/accounts/password_reset.html
templates/students/dashboard.html
```

### Pages To Build

```txt
/register/          Register page
/login/             Login page
/logout/            Logout action
/verify/            Account verification page
/password-reset/    Password reset page
/dashboard/         Student/parent dashboard
```

### Register Page Must Include

- First name
- Last name
- Email
- Phone number
- Password
- Confirm password
- Role selection
- Submit button
- Link to login

### Login Page Must Include

- Email or username field
- Password field
- Login button
- Link to register
- Link to password reset

### Student Dashboard Must Include

- Welcome message
- Search box that links to AI tutor search
- Recent bookings section
- Recommended tutors section
- Saved tutors placeholder

### Files This Person Will Mostly Touch

```txt
accounts/models.py
accounts/forms.py
accounts/views.py
accounts/urls.py
accounts/admin.py
templates/accounts/
templates/students/dashboard.html
```

### Done Means

- A user can register.
- A user can select a role.
- A user can login.
- A user can logout.
- A logged-in student can see the student dashboard.
- Users are redirected based on their role.

### Suggested Branch Name

```txt
feature/accounts-student-dashboard
```

## Task 3: Tutor Profiles, Subjects, Tutor Verification

This task owns everything related to tutors and tutor profile visibility.

### Main Responsibility

Allow tutors to create profiles, add subjects, upload verification documents, and appear in public tutor listings after verification.

### Backend Work

- Create `Tutor` model.
- Create `Subject` model.
- Create `TutorSubject` relationship model if needed.
- Create `TutorDocument` model.
- Tutor model should include:
  - User
  - Profile photo
  - Bio
  - Location
  - Hourly rate
  - Years of experience
  - Verification status
- Subject model should include:
  - Subject name
- Tutor document model should include:
  - Tutor
  - Document type
  - Document file/url
  - Verification status
- Create tutor profile form.
- Create tutor profile create/update view.
- Create tutor verification upload form.
- Create tutor dashboard view.
- Create public tutor list view.
- Create public tutor detail view.
- Add basic filters for tutor listing:
  - Subject
  - Location
  - Price
- Only show verified or approved tutors publicly when admin approval is ready.

### Frontend Work

Create these templates:

```txt
templates/tutors/dashboard.html
templates/tutors/profile_form.html
templates/tutors/verification.html
templates/tutors/tutor_list.html
templates/tutors/tutor_detail.html
```

### Pages To Build

```txt
/tutor/dashboard/       Tutor dashboard
/tutor/profile/         Tutor profile setup/edit
/tutor/verification/    Tutor verification upload
/tutors/                Public tutor listings
/tutors/<id>/           Public tutor profile details
```

### Tutor Dashboard Must Include

- Profile completion status
- Verification status
- Upcoming lessons placeholder
- Earnings placeholder
- Booking requests placeholder
- Link to edit profile
- Link to upload verification documents

### Tutor Profile Form Must Include

- Profile photo upload
- Bio
- Location
- Hourly rate
- Years of experience
- Subjects taught
- Qualifications
- Save button

### Verification Page Must Include

- Government ID upload
- Selfie upload
- Certificate upload
- Current verification status
- Submit button

### Tutor Listing Page Must Include

- Tutor cards
- Profile photo
- Name
- Subject
- Location
- Rate
- Verification badge
- View profile button
- Filter section

### Tutor Detail Page Must Include

- Profile photo
- Tutor name
- Bio
- Subjects
- Location
- Experience
- Hourly rate
- Reviews placeholder
- Verification badge
- Book tutor button

### Files This Person Will Mostly Touch

```txt
tutors/models.py
tutors/forms.py
tutors/views.py
tutors/urls.py
tutors/admin.py
templates/tutors/
media/
```

### Done Means

- A tutor can create or update their profile.
- A tutor can upload verification documents.
- Tutor profiles can be listed.
- A student can view tutor details.
- Tutor data can later be used by AI search and booking.

### Suggested Branch Name

```txt
feature/tutor-profiles-verification
```

## Task 4: AI Search, Tutor Discovery, Filters

This task owns natural language tutor search and normal tutor filtering.

### Main Responsibility

Allow students/parents to search for tutors using plain English and get useful tutor recommendations.

### Backend Work

- Create AI search views.
- Create search form.
- Accept natural language prompt from user.
- Connect to OpenAI API.
- Extract:
  - Subject
  - Level
  - Location
  - Preferred schedule if available
- Return extracted result as structured data.
- Query tutor profiles using extracted subject/location.
- Add fallback search if OpenAI API is not available.
- Add normal search filters:
  - Subject
  - Location
  - Minimum price
  - Maximum price
  - Experience
- Create recommendation logic.
- Display best tutor matches first.
- Handle empty results.
- Handle invalid or unclear search prompts.

### Frontend Work

Create these templates:

```txt
templates/search/find_tutor.html
templates/search/search_results.html
templates/search/no_results.html
```

### Pages To Build

```txt
/find-tutor/       AI tutor search page
/search-results/   Tutor search results page
```

### AI Search Page Must Include

- Large prompt input field
- Example prompt text
- Search button
- Optional filters section
- Loading state or simple searching message

### Search Results Page Must Include

- Original user prompt
- Extracted search details:
  - Subject
  - Level
  - Location
- Tutor result cards
- Filter sidebar or filter row
- Sort option placeholder
- Button to view tutor profile
- Button to book tutor

### No Results Page Must Include

- Friendly message
- Search again button
- Suggested subjects or locations placeholder

### Example Prompt

```txt
I need a Mathematics tutor for SS2 in Port Harcourt who can teach weekends.
```

### Expected Extracted Data

```json
{
  "subject": "Mathematics",
  "level": "SS2",
  "location": "Port Harcourt",
  "schedule": "weekends"
}
```

### Files This Person Will Mostly Touch

```txt
ai_search/forms.py
ai_search/views.py
ai_search/urls.py
ai_search/services.py
templates/search/
tutors/models.py
```

### Done Means

- A user can enter a natural language prompt.
- The system extracts search details.
- The system displays matching tutors.
- Normal filters work even if AI is not connected yet.
- Empty results are handled properly.

### Suggested Branch Name

```txt
feature/ai-search-discovery
```

## Task 5: Bookings, Payments, Reviews

This task owns the full booking, payment, and review flow.

### Main Responsibility

Allow students to book tutors, pay securely, allow tutors to accept/reject bookings, and allow students to review completed lessons.

### Backend Work

- Create `Booking` model.
- Create `Payment` model.
- Create `Review` model.
- Booking model should include:
  - Student
  - Tutor
  - Booking date
  - Lesson time
  - Status
  - Amount
- Booking statuses:
  - Pending
  - Accepted
  - Completed
  - Cancelled
- Payment model should include:
  - Booking
  - Amount
  - Commission
  - Tutor payout
  - Payment status
  - Paystack reference
- Review model should include:
  - Student
  - Tutor
  - Booking
  - Rating
  - Review text
- Create booking form.
- Create booking confirmation view.
- Create student booking history.
- Create tutor booking request page.
- Add accept booking logic.
- Add reject booking logic.
- Add complete booking logic.

- Integrate Paystack checkout.
- Verify Paystack payment.
- Calculate 15% platform commission.
- Calculate 85% tutor payout.
- Allow review only after completed booking.

### Frontend Work

Create these templates:

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

### Pages To Build

```txt
/book/<tutor_id>/              Book tutor page
/bookings/                     Student booking history
/tutor/bookings/               Tutor booking requests
/payment/<booking_id>/         Payment checkout
/payment/success/              Payment success page
/payment/failed/               Payment failed page
/reviews/add/<booking_id>/     Add review page
```

### Booking Page Must Include

- Tutor summary
- Date field
- Time field
- Lesson note field
- Lesson amount
- Confirm booking button

### Student Bookings Page Must Include

- Booking list
- Tutor name
- Date
- Time
- Status
- Amount
- Payment status
- Review button when lesson is completed

### Tutor Bookings Page Must Include

- Booking requests
- Student name
- Date
- Time
- Amount
- Accept button
- Reject button
- Complete button when lesson is done

### Payment Page Must Include

- Booking summary
- Total amount
- Platform payment notice
- Paystack payment button

### Review Page Must Include

- Rating input
- Review text field
- Submit review button

### Files This Person Will Mostly Touch

```txt
bookings/models.py
bookings/forms.py
bookings/views.py
bookings/urls.py
payments/models.py
payments/views.py
payments/urls.py
reviews/models.py
reviews/forms.py
reviews/views.py
reviews/urls.py
templates/bookings/
templates/payments/
templates/reviews/
```

### Done Means

- A student can book a tutor.
- A tutor can accept or reject a booking.
- A student can view booking history.
- A tutor can view booking requests.
- Payment flow is ready for Paystack.
- Commission and tutor payout are calculated.
- A student can review a completed lesson.

### Suggested Branch Name

```txt
feature/bookings-payments-reviews
```

## First Sprint Target

By the end of the first sprint, the team should have this basic flow working:

1. User can register and login.
2. Tutor can create a profile.
3. Student can browse tutors.
4. Student can search for tutors.
5. Student can book a tutor.
6. Admin can view basic dashboard pages.

Paystack and OpenAI can start as mock/demo versions first. After the main flow works, connect the real APIs.

## GitHub Workflow

Each person must work on their own branch.

```txt
leader/project-setup-dashboard
feature/accounts-student-dashboard
feature/tutor-profiles-verification
feature/ai-search-discovery
feature/bookings-payments-reviews
```

Before opening a pull request:

- Pull the latest `main` branch.
- Run the project locally.
- Test your own pages.
- Make sure your templates extend `base.html`.
- Make sure your URLs are connected.
- Make sure your forms submit correctly.
- Open a pull request.
- Project leader reviews before merge.

## Team Rule

Do not build only backend or only frontend. Each person must complete their full feature from database/model to view to template. That way, every task becomes a working part of the product.

