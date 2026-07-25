from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Avg, Count, Q, Sum
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from django.http import Http404
from accounts.decorators import tutor_required
from config.imagekit_utils import upload_file_in_memory, validate_file
from .models import Tutor, TutorDocument, Subject, CourseOffer
from bookings.models import Booking
from payments.models import PayoutInstallment
from reviews.models import Review
from .forms import TutorPersonalProfileForm, TutorPayoutForm, TutorDocumentForm, CourseOfferForm
from .geo_data import NIGERIAN_LGAS, DEFAULT_COUNTRY, WORLD_SUBDIVISIONS
from django.views.decorators.csrf import ensure_csrf_cookie
import json



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
            profile.profile_photo = upload_file_in_memory(photo, folder="/tutor_photos")

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
        return redirect('tutor_dashboard')
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

        profile.documents.all().delete()
        profile.verification_status = "pending"
        profile.user.is_verified = False
        profile.user.save(update_fields=["is_verified"])

        doc = form.save(commit=False)
        doc.tutor = profile
        doc.document_url = upload_file_in_memory(document_file, folder="/tutor_documents")
        doc.save()
        profile.save(update_fields=["verification_status"])
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
    mode_filter = request.GET.get('mode')
    search_query = request.GET.get('q', '').strip()
    currency_filter = request.GET.get('currency')
    sort_by = request.GET.get('sort', 'newest')

    offers_qs = CourseOffer.objects.filter(is_active=True, tutor__verification_status="approved", tutor__is_publicly_visible=True).select_related('tutor__user__user', 'subject')

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
            Q(subject__subject_name__icontains=search_query) |
            Q(tutor__user__user__first_name__icontains=search_query) |
            Q(tutor__user__user__last_name__icontains=search_query)
        )

    if sort_by == 'price_low':
        offers_qs = offers_qs.order_by('daily_rate')
    elif sort_by == 'price_high':
        offers_qs = offers_qs.order_by('-daily_rate')
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


