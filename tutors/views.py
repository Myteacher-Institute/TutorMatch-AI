from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from accounts.decorators import tutor_required
from config.imagekit_utils import upload_file_in_memory, validate_file
from .models import Tutor, TutorDocument
from .forms import TutorProfileForm, TutorDocumentForm


@tutor_required
def tutor_dashboard(request):
    profile, created = Tutor.objects.get_or_create(user=request.user.profile)
    return render(request, 'tutors/dashboard.html', {'profile': profile, 'active_tab': 'dashboard'})


@tutor_required
def tutor_profile(request):
    profile, created = Tutor.objects.get_or_create(user=request.user.profile)
    form = TutorProfileForm(request.POST or None, request.FILES or None, instance=profile)

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
        form.save_m2m()
        messages.success(request, 'Profile updated successfully.')
        return redirect('tutor_dashboard')

    return render(request, 'tutors/profile_form.html', {'form': form, 'profile': profile, 'active_tab': 'profile'})


@tutor_required
def tutor_verification(request):
    profile, created = Tutor.objects.get_or_create(user=request.user.profile)
    form = TutorDocumentForm(request.POST or None, request.FILES or None)

    if form.is_valid():
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

        doc = form.save(commit=False)
        doc.tutor = profile
        doc.document_url = upload_file_in_memory(document_file, folder="/tutor_documents")
        doc.save()
        messages.success(request, 'Document uploaded successfully.')
        return redirect('tutor_verification')

    documents = profile.documents.all()
    return render(request, 'tutors/verification.html', {
        'form': form,
        'documents': documents,
        'profile': profile,
        'active_tab': 'verification',
    })


def tutor_list(request):
    tutors = Tutor.objects.filter(is_publicly_visible=True)

    subject_filter = request.GET.get('subject')
    location_filter = request.GET.get('location')
    max_rate = request.GET.get('max_rate')

    if subject_filter:
        tutors = tutors.filter(subjects__subject_name__icontains=subject_filter)
    if location_filter:
        tutors = tutors.filter(location__icontains=location_filter)
    if max_rate:
        tutors = tutors.filter(hourly_rate__lte=max_rate)

    return render(request, 'tutors/tutor_list.html', {'tutors': tutors})


def tutor_detail(request, tutor_id):
    tutor = get_object_or_404(Tutor.objects.select_related("user__user").prefetch_related("subjects"), id=tutor_id)
    return render(request, 'tutors/tutor_detail.html', {'tutor': tutor})
