from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Avg, Count, Q, Sum
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from django.http import Http404
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from accounts.decorators import tutor_required
from config.imagekit_utils import upload_file_in_memory, validate_file
from .models import Tutor, TutorDocument, Subject, CourseOffer, IntroCallRequest
from bookings.models import Booking
from payments.models import PayoutInstallment
from reviews.models import Review
from .forms import TutorPersonalProfileForm, TutorPayoutForm, TutorDocumentForm, CourseOfferForm
from .geo_data import NIGERIAN_LGAS, DEFAULT_COUNTRY, WORLD_SUBDIVISIONS
import json
import logging

logger = logging.getLogger(__name__)



@tutor_required
def tutor_dashboard(request):
    profile, created = Tutor.objects.get_or_create(user=request.user.profile)
    bookings_count = Booking.objects.filter(tutor=profile, payments__payment_status="paid").distinct().count()
    teaching_services = CourseOffer.objects.filter(tutor=profile)
    upcoming_bookings = (
        Booking.objects.filter(
            tutor=profile,
            status="accepted",
            booking_date__gte=timezone.localdate(),
            payments__payment_status="paid",
        )
        .select_related("student__user")
        .distinct()
        .order_by("booking_date", "lesson_time")
    )
    return render(request, 'tutors/dashboard.html', {
        'profile': profile,
        'bookings_count': bookings_count,
        'teaching_services': teaching_services,
        'current_balance': profile.current_balance,
        'pending_earnings': profile.pending_earnings,
        'total_paid_out': profile.total_paid_out,
        'next_payout_date': profile.next_payout_date,
        'upcoming_installments': profile.upcoming_payout_installments,
        'upcoming_bookings': upcoming_bookings,
        'active_tab': 'dashboard',
    })


@tutor_required
def tutor_profile(request):
    profile, created = Tutor.objects.get_or_create(user=request.user.profile)
    
    if request.method == 'POST':
        form = TutorPersonalProfileForm(request.POST, request.FILES, instance=profile)
    else:
        form = TutorPersonalProfileForm(instance=profile)

    if form.is_valid():
        profile = form.save(commit=False)
        photo = form.cleaned_data.get('profile_photo_upload')
        if photo:
            is_valid_file, error = validate_file(photo)
            if not is_valid_file:
                form.add_error('profile_photo_upload', error)
                return render(request, 'tutors/profile_form.html', {'form': form, 'profile': profile, 'active_tab': 'profile'})
            uploaded_photo = upload_file_in_memory(photo, folder="/tutor_photos")
            if uploaded_photo:
                profile.profile_photo = uploaded_photo
            else:
                messages.warning(request, 'Failed to upload new profile photo to cloud storage. Please try again.')

        profile.save()
        
        subjects_input = form.cleaned_data.get('subjects_input')
        if subjects_input:
            from .models import Subject
            subject_names = [s.strip() for s in subjects_input.split(',') if s.strip()]
            profile.subjects.clear()
            for name in subject_names:
                subj, _ = Subject.objects.get_or_create(subject_name=name)
                profile.subjects.add(subj)

        messages.success(request, 'Personal profile updated successfully.')
        return redirect('tutor_profile')
    else:
        # If the form is not valid and method is POST, show the errors
        if request.method == 'POST':
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{form.fields[field].label if field in form.fields and form.fields[field].label else field}: {error}")


    return render(request, 'tutors/profile_form.html', {
        'form': form,
        'profile': profile,
        'active_tab': 'profile',
        'world_subdivisions_json': json.dumps(WORLD_SUBDIVISIONS),
        'lgas_json': json.dumps(NIGERIAN_LGAS),
        'default_country': DEFAULT_COUNTRY,
    })


@tutor_required
def tutor_payout_settings(request):
    profile, created = Tutor.objects.get_or_create(user=request.user.profile)
    if request.method == 'POST':
        form = TutorPayoutForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Payout settings updated successfully.')
            return redirect('tutor_payout_settings')
    else:
        form = TutorPayoutForm(instance=profile)

    return render(request, 'tutors/payout_settings.html', {
        'form': form,
        'profile': profile,
        'active_tab': 'payout',
    })


@tutor_required
def tutor_verification(request):
    profile, created = Tutor.objects.get_or_create(user=request.user.profile)
    form = TutorDocumentForm(request.POST or None, request.FILES or None)

    if form.is_valid():
        existing_approved = profile.documents.filter(verification_status="approved").exists()
        if existing_approved:
            messages.error(request, 'Your document has already been verified. Cannot re-upload.')
            return redirect('tutor_verification')

        document_file = form.cleaned_data.get('document_file')
        is_valid_file, error = validate_file(document_file)
        if not is_valid_file:
            form.add_error('document_file', error)
            return render(request, 'tutors/verification.html', {
                'form': form,
                'documents': profile.documents.all(),
                'profile': profile,
                'active_tab': 'verification',
            })

        uploaded_url = upload_file_in_memory(document_file, folder="/tutor_documents")
        if not uploaded_url:
            messages.error(request, 'Failed to upload document to cloud storage. Please verify your file format and network, then try again.')
            return render(request, 'tutors/verification.html', {
                'form': form,
                'documents': profile.documents.all(),
                'profile': profile,
                'active_tab': 'verification',
            })

        profile.documents.all().delete()
        profile.verification_status = "pending"

        doc = form.save(commit=False)
        doc.tutor = profile
        doc.document_url = uploaded_url
        doc.save()
        profile.save(update_fields=["verification_status"])
        try:
            from accounts.account_emails import send_admin_tutor_documents_submitted_notification
            send_admin_tutor_documents_submitted_notification(request, profile)
        except Exception:
            pass
        messages.success(request, 'Document uploaded successfully.')
        return redirect('tutor_verification')

    documents = profile.documents.all()
    return render(request, 'tutors/verification.html', {
        'form': form,
        'documents': documents,
        'profile': profile,
        'active_tab': 'verification',
    })


@ensure_csrf_cookie
def tutor_list(request):
    tutors_qs = Tutor.objects.filter(is_publicly_visible=True, verification_status="approved")

    query = request.GET.get('q', '').strip()
    subject_filter = request.GET.get('subject')
    location_filter = request.GET.get('location')
    max_rate = request.GET.get('max_rate')
    sort = request.GET.get('sort', 'recommended')

    if query:
        tutors_qs = tutors_qs.filter(
            Q(user__user__first_name__icontains=query)
            | Q(user__user__last_name__icontains=query)
            | Q(user__user__username__icontains=query)
            | Q(subjects__subject_name__icontains=query)
            | Q(location__icontains=query)
            | Q(bio__icontains=query)
        )

    if subject_filter:
        tutors_qs = tutors_qs.filter(subjects__subject_name__icontains=subject_filter)
    if location_filter:
        tutors_qs = tutors_qs.filter(location__icontains=location_filter)
    if max_rate:
        tutors_qs = tutors_qs.filter(rate_amount__lte=max_rate)

    tutors_qs = tutors_qs.annotate(
        avg_rating=Avg("tutor_reviews__rating"),
        review_count=Count("tutor_reviews", distinct=True),
    ).distinct()

    if sort == "rate_low":
        tutors_qs = tutors_qs.order_by("rate_amount", "-avg_rating", "user__user__first_name")
    elif sort == "rate_high":
        tutors_qs = tutors_qs.order_by("-rate_amount", "-avg_rating", "user__user__first_name")
    elif sort == "rating":
        tutors_qs = tutors_qs.order_by("-avg_rating", "-review_count", "user__user__first_name")
    elif sort == "experience":
        tutors_qs = tutors_qs.order_by("-years_experience", "-avg_rating", "user__user__first_name")
    else:
        tutors_qs = tutors_qs.order_by("-is_publicly_visible", "-avg_rating", "user__user__first_name")

    paginator = Paginator(tutors_qs, 9)
    page_number = request.GET.get("page")
    tutors = paginator.get_page(page_number)

    subjects = Subject.objects.filter(tutors__is_publicly_visible=True, tutors__verification_status="approved").distinct().order_by("subject_name")
    locations = (
        Tutor.objects.filter(is_publicly_visible=True, verification_status="approved")
        .exclude(location="")
        .values_list("location", flat=True)
        .distinct()
        .order_by("location")
    )

    return render(request, 'tutors/tutor_list.html', {
        'tutors': tutors,
        'page_obj': tutors,
        'subjects': subjects,
        'locations': locations,
    })


@ensure_csrf_cookie
def tutor_detail(request, tutor_id):
    tutor = get_object_or_404(
        Tutor.objects.select_related("user__user").prefetch_related("subjects"),
        id=tutor_id,
    )

    if tutor.verification_status != "approved" or not tutor.is_publicly_visible:
        is_owner = (
            request.user.is_authenticated
            and tutor.user
            and tutor.user.user
            and request.user == tutor.user.user
        )
        if not is_owner:
            raise Http404("No Tutor matches the given query.")

    from tutors.models import CourseOffer
    course_offers = CourseOffer.objects.filter(tutor=tutor, is_active=True).select_related("subject")

    reviews_list = Review.objects.filter(tutor=tutor).select_related("student__user").order_by("-created_at")
    paginator = Paginator(reviews_list, 5)
    page_number = request.GET.get("page")
    reviews = paginator.get_page(page_number)
    return render(request, 'tutors/tutor_detail.html', {
        'tutor': tutor,
        'reviews': reviews,
        'course_offers': course_offers,
    })


# ==========================================
# TUTOR COURSE OFFER MANAGEMENT VIEWS
# ==========================================

@tutor_required
def course_offer_list(request):
    profile, _ = Tutor.objects.get_or_create(user=request.user.profile)
    offers = CourseOffer.objects.filter(tutor=profile).select_related("subject")
    return render(request, 'tutors/course_offer_manage.html', {
        'profile': profile,
        'offers': offers,
        'active_tab': 'offers',
    })


@tutor_required
def course_offer_create(request):
    profile, _ = Tutor.objects.get_or_create(user=request.user.profile)
    if request.method == 'POST':
        form = CourseOfferForm(request.POST, request.FILES)
        if form.is_valid():
            offer = form.save(commit=False)
            offer.tutor = profile
            offer.save()
            messages.success(request, f'Course "{offer.title}" created successfully!')
            return redirect('course_offer_list')
    else:
        form = CourseOfferForm()

    return render(request, 'tutors/course_offer_form.html', {
        'form': form,
        'profile': profile,
        'is_edit': False,
        'active_tab': 'offers',
    })


@tutor_required
def course_offer_edit(request, offer_id):
    profile, _ = Tutor.objects.get_or_create(user=request.user.profile)
    offer = get_object_or_404(CourseOffer, id=offer_id, tutor=profile)
    
    if request.method == 'POST':
        form = CourseOfferForm(request.POST, request.FILES, instance=offer)
        if form.is_valid():
            form.save()
            messages.success(request, f'Course "{offer.title}" updated successfully!')
            return redirect('course_offer_list')
    else:
        form = CourseOfferForm(instance=offer)

    return render(request, 'tutors/course_offer_form.html', {
        'form': form,
        'offer': offer,
        'profile': profile,
        'is_edit': True,
        'active_tab': 'offers',
    })


@tutor_required
def course_offer_delete(request, offer_id):
    profile, _ = Tutor.objects.get_or_create(user=request.user.profile)
    offer = get_object_or_404(CourseOffer, id=offer_id, tutor=profile)
    if request.method == 'POST':
        offer.delete()
        messages.success(request, f'Course "{offer.title}" deleted.')
    return redirect('course_offer_list')


# ==========================================
# PUBLIC COURSE MARKETPLACE VIEWS
# ==========================================

def course_list(request):
    subject_id = request.GET.get('subject')
    category_filter = request.GET.get('category')
    mode_filter = request.GET.get('mode')
    search_query = request.GET.get('q', '').strip()
    currency_filter = request.GET.get('currency')
    sort_by = request.GET.get('sort', 'newest')

    offers_qs = CourseOffer.objects.filter(is_active=True, tutor__verification_status="approved", tutor__is_publicly_visible=True).select_related('tutor__user__user', 'subject')

    if category_filter:
        offers_qs = offers_qs.filter(category__icontains=category_filter)
    if subject_id:
        offers_qs = offers_qs.filter(subject_id=subject_id)
    if mode_filter:
        offers_qs = offers_qs.filter(delivery_mode=mode_filter)
    if currency_filter:
        offers_qs = offers_qs.filter(currency=currency_filter)
    if search_query:
        offers_qs = offers_qs.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__icontains=search_query) |
            Q(subject__subject_name__icontains=search_query) |
            Q(tutor__user__user__first_name__icontains=search_query) |
            Q(tutor__user__user__last_name__icontains=search_query)
        )

    if sort_by == 'price_low':
        offers_qs = offers_qs.order_by('monthly_fee')
    elif sort_by == 'price_high':
        offers_qs = offers_qs.order_by('-monthly_fee')
    else:
        offers_qs = offers_qs.order_by('-created_at')

    paginator = Paginator(offers_qs, 9)
    page_number = request.GET.get('page')
    offers = paginator.get_page(page_number)

    subjects = Subject.objects.filter(course_offers__is_active=True).distinct()

    return render(request, 'courses/course_list.html', {
        'offers': offers,
        'page_obj': offers,
        'subjects': subjects,
        'selected_subject': subject_id,
        'selected_category': category_filter,
        'selected_mode': mode_filter,
        'selected_currency': currency_filter,
        'search_query': search_query,
        'sort_by': sort_by,
    })


def course_detail(request, offer_id):
    offer = get_object_or_404(
        CourseOffer.objects.select_related('tutor__user__user', 'subject'),
        id=offer_id,
    )
    tutor = offer.tutor
    reviews = Review.objects.filter(tutor=tutor).select_related('student__user').order_by('-created_at')[:5]

    return render(request, 'courses/course_detail.html', {
        'offer': offer,
        'tutor': tutor,
        'reviews': reviews,
    })


@require_POST
def request_intro_call(request, tutor_id):
    tutor = get_object_or_404(Tutor, id=tutor_id)
    course_offer_id = request.POST.get("course_offer_id")
    student_name = request.POST.get("student_name", "").strip()
    student_email = request.POST.get("student_email", "").strip()
    phone_number = request.POST.get("phone_number", "").strip()
    preferred_call_time = request.POST.get("preferred_call_time", "").strip()
    notes = request.POST.get("notes", "").strip()

    if not student_name or not phone_number:
        messages.error(request, "Please provide your name and phone/WhatsApp number for the 15-minute call.")
        if course_offer_id:
            return redirect("course_detail", offer_id=course_offer_id)
        return redirect("tutor_detail", tutor_id=tutor.id)

    course_offer = None
    if course_offer_id:
        course_offer = CourseOffer.objects.filter(id=course_offer_id).first()

    intro_call = IntroCallRequest.objects.create(
        tutor=tutor,
        course_offer=course_offer,
        student_name=student_name,
        student_email=student_email,
        phone_number=phone_number,
        preferred_call_time=preferred_call_time,
        notes=notes,
    )

    try:
        from accounts.email_services import send_transactional_email
        tutor_email = tutor.user.user.email if tutor.user and tutor.user.user else None
        if tutor_email:
            subject = f"📞 New 15-Min Free Discovery Call Request from {student_name}"
            content = f"""
Hello {tutor.first_name},

{student_name} has requested a FREE 15-Minute Discovery Call with you on MyteacherConnect!

Details:
- Student/Parent Name: {student_name}
- Phone / WhatsApp: {phone_number}
- Email: {student_email or 'Not provided'}
- Preferred Call Time: {preferred_call_time or 'Anytime'}
- Course Interest: {course_offer.title if course_offer else 'General Tutoring'}
- Note: {notes or 'No additional notes'}

Please reach out to them via WhatsApp or Phone to conduct your 15-minute intro call.

REMINDER: Discovery calls can take place on Phone, Zoom, or WhatsApp, but ALL course payments MUST be processed through MyteacherConnect to be protected by our 30-Day Escrow Payout Policy.

Best regards,
MyteacherConnect Team
"""
            send_transactional_email(tutor_email, subject, content)
    except Exception as e:
        logger.warning(f"Could not send intro call email notification: {e}")

    messages.success(
        request,
        f"🎉 Your 15-Minute Free Discovery Call request was sent to {tutor.get_full_name}! They will contact you shortly on {phone_number}."
    )
    if course_offer_id:
        return redirect("course_detail", offer_id=course_offer_id)
    return redirect("tutor_detail", tutor_id=tutor.id)


