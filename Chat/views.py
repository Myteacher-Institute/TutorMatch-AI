from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages # Import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator

from .models import ChatSession, ChatMessage
from bookings.models import Booking
from accounts.models import UserProfile
from tutors.models import Tutor

CHAT_LIST_PAGE_SIZE = 15


def _user_can_access_booking_chat(user, booking):
    # Staff users (admins) can access any chat
    if user.is_staff:
        return True
    
    return (
        hasattr(user, "profile")
        and (user.profile == booking.student or user.profile == booking.tutor.user)
    )


def _chat_users_for_booking(booking):
    return booking.student.user, booking.tutor.user.user


def _paginate_chat_sessions(request, chat_sessions):
    paginator = Paginator(chat_sessions, CHAT_LIST_PAGE_SIZE)
    return paginator.get_page(request.GET.get('page'))

@login_required
def chat_view(request, booking_id):
    booking = get_object_or_404(
        Booking.objects.select_related("tutor__user__user__profile__tutor_profile", "student__user__profile"),
        id=booking_id
    )

    if not _user_can_access_booking_chat(request.user, booking):
        messages.error(request, "You are not authorized to view this chat.")
        return redirect('home')

    student_user_obj, tutor_user_obj = _chat_users_for_booking(booking)

    session, created = ChatSession.objects.get_or_create(
        booking=booking,
        student=student_user_obj,
        tutor=tutor_user_obj
    )

    chat_messages = ChatMessage.objects.filter(session=session).order_by('timestamp')

    # Mark messages as read if the recipient is viewing them
    for message in chat_messages:
        if message.sender != request.user and not message.is_read:
            message.is_read = True
            message.save()

    context = {
        'booking': booking,
        'chat_session': session,
        'chat_messages_list': chat_messages,
        # Determine the other party's User object for display
        'other_party': tutor_user_obj if request.user == student_user_obj else student_user_obj,
    }
    print(f"DEBUG: other_party: {context['other_party']}")
    if hasattr(context['other_party'], 'profile'):
        print(f"DEBUG: other_party.profile: {context['other_party'].profile}")
        if hasattr(context['other_party'].profile, 'tutor_profile'):
            print(f"DEBUG: other_party.profile.tutor_profile: {context['other_party'].profile.tutor_profile}")
            print(f"DEBUG: other_party.profile.tutor_profile.hourly_rate: {context['other_party'].profile.tutor_profile.hourly_rate}")
    return render(request, 'Chat/chat.html', context)


@login_required
def send_message(request, booking_id):
    if request.method == 'POST':
        booking = get_object_or_404(
            Booking.objects.select_related("tutor__user__user", "student__user"),
            id=booking_id
        )

        if not _user_can_access_booking_chat(request.user, booking):
            return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)

        student_user_obj, tutor_user_obj = _chat_users_for_booking(booking)

        session, created = ChatSession.objects.get_or_create(
            booking=booking,
            student=student_user_obj,
            tutor=tutor_user_obj,
        )

        message_content = request.POST.get('message', '').strip()
        if message_content:
            new_message = ChatMessage.objects.create(
                session=session,
                sender=request.user,
                message=message_content
            )
            session.save() # Explicitly save the session to update 'updated_at'
            # Render the new message as an HTML fragment
            context = {
                'chat_session': session,
                'chat_messages_list': [new_message],
            }
            return render(request, 'Chat/messages_list.html', context)
    return HttpResponse(status=204) # No content if not a POST or message is empty


@login_required
def tutor_chat_list(request):
    # Ensure the logged-in user is a tutor
    if not (hasattr(request.user, 'profile') and request.user.profile.role == UserProfile.ROLE_TUTOR):
        messages.error(request, "You are not authorized to view this page.")
        return redirect('home')

    # Get chat sessions where the current user is the tutor
    # Order by the latest message or session update for active chats
    chat_sessions = _paginate_chat_sessions(
        request,
        ChatSession.objects.filter(tutor=request.user).order_by('-updated_at'),
    )

    tutor_obj = get_object_or_404(Tutor, user=request.user.profile)

    context = {
        'chat_sessions': chat_sessions,
        'page_obj': chat_sessions,
        'tutor_profile': tutor_obj, # Pass the tutor's profile
        'active_tab': 'chats',
    }
    return render(request, 'Chat/tutor_chat_list.html', context)

@login_required
def get_new_messages(request, booking_id, last_message_id):
    booking = get_object_or_404(
        Booking.objects.select_related("tutor__user__user", "student__user"),
        id=booking_id
    )

    if not _user_can_access_booking_chat(request.user, booking):
        return HttpResponse(status=403)

    student_user_obj, tutor_user_obj = _chat_users_for_booking(booking)

    session, created = ChatSession.objects.get_or_create(
        booking=booking,
        student=student_user_obj,
        tutor=tutor_user_obj,
    )

    new_messages = ChatMessage.objects.filter(session=session, id__gt=last_message_id).order_by('timestamp')

    # Mark new messages as read if the recipient is viewing them
    for message in new_messages:
        if message.sender != request.user and not message.is_read:
            message.is_read = True
            message.save()

    context = {
        'chat_session': session,
        'chat_messages_list': new_messages,
    }
    return render(request, 'Chat/messages_list.html', context)


@login_required
def admin_chat_list(request):
    if not request.user.is_superuser:
        messages.error(request, "You are not authorized to view this page.")
        return redirect('home')

    chat_sessions = _paginate_chat_sessions(
        request,
        ChatSession.objects.all().order_by('-updated_at'),
    )

    context = {
        'chat_sessions': chat_sessions,
        'page_obj': chat_sessions,
        'active_tab': 'chats',
    }
    return render(request, 'Chat/admin_chat_list.html', context)


@login_required
def student_chat_list(request):
    # Ensure the logged-in user is a student
    if not (hasattr(request.user, 'profile') and request.user.profile.role == UserProfile.ROLE_STUDENT):
        messages.error(request, "You are not authorized to view this page.")
        return redirect('home')

    # Get chat sessions where the current user is the student
    chat_sessions = _paginate_chat_sessions(
        request,
        ChatSession.objects.filter(student=request.user).order_by('-updated_at'),
    )

    context = {
        'chat_sessions': chat_sessions,
        'page_obj': chat_sessions,
        'student_profile': request.user.profile, # Pass the student's profile
        'active_tab': 'chats',
    }
    return render(request, 'Chat/student_chat_list.html', context)
