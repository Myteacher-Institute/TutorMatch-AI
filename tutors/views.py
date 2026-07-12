from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Avg, Count, Q, Sum
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from django.http import Http404
from accounts.decorators import tutor_required
from config.imagekit_utils import upload_file_in_memory, validate_file
from .models import Tutor, TutorDocument, Subject
from bookings.models import Booking
from payments.models import Payment
from reviews.models import Review
from .forms import TutorProfileForm, TutorDocumentForm
from .geo_data import NIGERIAN_LGAS, DEFAULT_COUNTRY
from django.views.decorators.csrf import ensure_csrf_cookie
import json


@tutor_required
def tutor_dashboard(request):
    profile, created = Tutor.objects.get_or_create(user=request.user.profile)
    bookings_count = Booking.objects.filter(tutor=profile, payments__payment_status="paid").distinct().count()
    total_earnings = Payment.objects.filter(
        booking__tutor=profile, payment_status="released"
    ).aggregate(total=Sum("tutor_payout"))["total"] or 0
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
    return render(request, 'tutors/dashboard.html', 
                  {'profile': profile, 
                   'bookings_count': bookings_count,
                   'total_earnings': total_earnings,
                   'upcoming_bookings': upcoming_bookings,
                   'active_tab': 'dashboard'})


@tutor_required
def tutor_profile(request):
    profile, created = Tutor.objects.get_or_create(user=request.user.profile)
    
    if request.method == 'POST':
        form = TutorProfileForm(request.POST, request.FILES, instance=profile)
    else:
        form = TutorProfileForm(instance=profile)
        existing_subjects = profile.subjects.values_list('subject_name', flat=True)
        form.fields['subjects_input'].initial = ', '.join(existing_subjects)

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
        subjects_input = form.cleaned_data.get('subjects_input', '')
        subject_names = [s.strip() for s in subjects_input.split(',') if s.strip()]
        subject_objs = []
        for name in subject_names:
            subject, _ = Subject.objects.get_or_create(subject_name=name)
            subject_objs.append(subject)
        profile.subjects.set(subject_objs)
        messages.success(request, 'Profile updated successfully.')
        return redirect('tutor_dashboard')

    return render(request, 'tutors/profile_form.html', {
        'form': form,
        'profile': profile,
        'active_tab': 'profile',
        'lgas_json': json.dumps(NIGERIAN_LGAS),
        'default_country': DEFAULT_COUNTRY,
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
        tutors_qs = tutors_qs.filter(hourly_rate__lte=max_rate)

    tutors_qs = tutors_qs.annotate(
        avg_rating=Avg("tutor_reviews__rating"),
        review_count=Count("tutor_reviews", distinct=True),
    ).distinct()

    if sort == "rate_low":
        tutors_qs = tutors_qs.order_by("hourly_rate", "-avg_rating", "user__user__first_name")
    elif sort == "rate_high":
        tutors_qs = tutors_qs.order_by("-hourly_rate", "-avg_rating", "user__user__first_name")
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

    reviews_list = Review.objects.filter(tutor=tutor).select_related("student__user").order_by("-created_at")
    paginator = Paginator(reviews_list, 5)
    page_number = request.GET.get("page")
    reviews = paginator.get_page(page_number)
    return render(request, 'tutors/tutor_detail.html', {'tutor': tutor, 'reviews': reviews})
