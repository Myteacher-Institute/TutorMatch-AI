from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages # Import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.db.models import Count, Q, Value
from django.db.models.functions import Concat, Coalesce
from django.core.paginator import Paginator
from django.contrib.sessions.models import Session
from django.utils import timezone

from .models import ChatSession, ChatMessage
from bookings.models import Booking
from accounts.models import UserProfile
from tutors.models import Tutor

CHAT_LIST_PAGE_SIZE = 10


def _is_admin_viewer(user):
    return (
        user.is_staff
        or user.is_superuser
        or getattr(getattr(user, 'profile', None), 'role', None) == 'admin'
    )


def _user_can_access_booking_chat(user, booking):
    # Staff users (admins) can access any chat
    if user.is_staff:
        return True

    if not hasattr(user, "profile"):
        return False

    is_student = user.profile == booking.student
    is_tutor = user.profile == booking.tutor.user
    has_paid = booking.payments.filter(payment_status="paid").exists()

    if is_student:
        return has_paid

    if is_tutor:
        # Tutors can always access and reply to a booking's chat,
        # even before the booking has been accepted.
        return True

    return False


def _chat_users_for_booking(booking):
    return booking.student.user, booking.tutor.user.user


def _paginate_chat_sessions(request, chat_sessions):
    paginator = Paginator(chat_sessions, CHAT_LIST_PAGE_SIZE)
    return paginator.get_page(request.GET.get('page'))


def _with_unread_counts(user, chat_sessions):
    unread_filter = Q(messages__is_read=False)

    if not user.is_staff:
        unread_filter &= ~Q(messages__sender=user)

    return chat_sessions.annotate(unread_count=Count('messages', filter=unread_filter))


def _mark_messages_read_for_participant(user, session, messages_queryset):
    if user not in (session.student, session.tutor):
        return

    messages_queryset.filter(is_read=False).exclude(sender=user).update(is_read=True)


def _get_online_user_ids():
    now = timezone.now()
    active_sessions = Session.objects.filter(expire_date__gt=now)
    online_ids = set()
    for session in active_sessions:
        data = session.get_decoded()
        user_id = data.get('_auth_user_id')
        if user_id:
            online_ids.add(int(user_id))
    return online_ids


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

    _mark_messages_read_for_participant(request.user, session, chat_messages)

    context = {
        'booking': booking,
        'chat_session': session,
        'chat_messages_list': chat_messages,
        # Determine the other party's User object for display
        'other_party': tutor_user_obj if request.user == student_user_obj else student_user_obj,
        'tutor_profile': getattr(tutor_user_obj.profile, 'tutor_profile', None),
        'is_admin': _is_admin_viewer(request.user),
    }
    if request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.role == 'student':
        template = 'Chat/chat_student.html'
    else:
        template = 'Chat/chat.html'
    return render(request, template, context)


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
                'is_admin': _is_admin_viewer(request.user),
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
    base_qs = ChatSession.objects.filter(tutor=request.user).order_by('-updated_at')
    unread_filter = Q(messages__is_read=False) & ~Q(messages__sender=request.user)
    total_unread = base_qs.annotate(unread_count=Count('messages', filter=unread_filter)).filter(unread_count__gt=0).count()

    query = request.GET.get('q', '').strip()
    if query:
        search_q = Q(
            student__first_name__icontains=query
        ) | Q(
            student__last_name__icontains=query
        ) | Q(
            student__username__icontains=query
        ) | Q(
            student__email__icontains=query
        )
        try:
            booking_id = int(query)
            search_q |= Q(booking__id=booking_id)
        except (ValueError, TypeError):
            pass

        identity_matches = base_qs.filter(search_q).distinct()
        if identity_matches.exists():
            base_qs = identity_matches
        else:
            base_qs = base_qs.filter(messages__message__icontains=query).distinct()

    chat_sessions = _paginate_chat_sessions(
        request,
        _with_unread_counts(
            request.user,
            base_qs,
        ),
    )

    tutor_obj = get_object_or_404(Tutor, user=request.user.profile)

    context = {
        'chat_sessions': chat_sessions,
        'page_obj': chat_sessions,
        'tutor_profile': tutor_obj, # Pass the tutor's profile
        'active_tab': 'chats',
        'total_unread': total_unread,
        'search_query': query,
        'online_user_ids': _get_online_user_ids(),
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

    _mark_messages_read_for_participant(request.user, session, new_messages)

    context = {
        'chat_session': session,
        'chat_messages_list': new_messages,
        'is_admin': _is_admin_viewer(request.user),
    }
    return render(request, 'Chat/messages_list.html', context)


@login_required
def admin_chat_list(request):
    if not request.user.is_superuser:
        messages.error(request, "You are not authorized to view this page.")
        return redirect('home')

    base_qs = ChatSession.objects.all().order_by('-updated_at')
    unread_filter = Q(messages__is_read=False) & ~Q(messages__sender=request.user)
    total_unread = base_qs.annotate(unread_count=Count('messages', filter=unread_filter)).filter(unread_count__gt=0).count()

    query = request.GET.get('q', '').strip()
    if query:
        base_qs = base_qs.annotate(
            student_full_name=Coalesce(Concat('student__first_name', Value(' '), 'student__last_name'), Value('')),
            tutor_full_name=Coalesce(Concat('tutor__first_name', Value(' '), 'tutor__last_name'), Value('')),
        )
        search_q = Q(
            student__first_name__icontains=query
        ) | Q(
            student__last_name__icontains=query
        ) | Q(
            student__username__icontains=query
        ) | Q(
            student__email__icontains=query
        ) | Q(
            student_full_name__icontains=query
        ) | Q(
            tutor__first_name__icontains=query
        ) | Q(
            tutor__last_name__icontains=query
        ) | Q(
            tutor__username__icontains=query
        ) | Q(
            tutor__email__icontains=query
        ) | Q(
            tutor_full_name__icontains=query
        )
        try:
            booking_id = int(query)
            search_q |= Q(booking__id=booking_id)
        except (ValueError, TypeError):
            pass

        identity_matches = base_qs.filter(search_q).distinct()
        if identity_matches.exists():
            base_qs = identity_matches
        else:
            base_qs = base_qs.filter(messages__message__icontains=query).distinct()

    chat_sessions = _paginate_chat_sessions(
        request,
        _with_unread_counts(
            request.user,
            base_qs,
        ),
    )

    context = {
        'chat_sessions': chat_sessions,
        'page_obj': chat_sessions,
        'active_tab': 'chats',
        'total_unread': total_unread,
        'search_query': query,
        'online_user_ids': _get_online_user_ids(),
    }
    return render(request, 'Chat/admin_chat_list.html', context)


@login_required
def student_chat_list(request):
    # Ensure the logged-in user is a student
    if not (hasattr(request.user, 'profile') and request.user.profile.role == UserProfile.ROLE_STUDENT):
        messages.error(request, "You are not authorized to view this page.")
        return redirect('home')

    # Get chat sessions where the current user is the student
    base_qs = ChatSession.objects.filter(student=request.user).order_by('-updated_at')
    unread_filter = Q(messages__is_read=False) & ~Q(messages__sender=request.user)
    total_unread = base_qs.annotate(unread_count=Count('messages', filter=unread_filter)).filter(unread_count__gt=0).count()

    query = request.GET.get('q', '').strip()
    if query:
        base_qs = base_qs.annotate(
            tutor_full_name=Coalesce(Concat('tutor__first_name', Value(' '), 'tutor__last_name'), Value('')),
        )
        search_q = Q(
            tutor__first_name__icontains=query
        ) | Q(
            tutor__last_name__icontains=query
        ) | Q(
            tutor__username__icontains=query
        ) | Q(
            tutor__email__icontains=query
        ) | Q(
            tutor_full_name__icontains=query
        )
        try:
            booking_id = int(query)
            search_q |= Q(booking__id=booking_id)
        except (ValueError, TypeError):
            pass

        identity_matches = base_qs.filter(search_q).distinct()
        if identity_matches.exists():
            base_qs = identity_matches
        else:
            base_qs = base_qs.filter(messages__message__icontains=query).distinct()

    chat_sessions = _paginate_chat_sessions(
        request,
        _with_unread_counts(
            request.user,
            base_qs,
        ),
    )

    context = {
        'chat_sessions': chat_sessions,
        'page_obj': chat_sessions,
        'student_profile': request.user.profile, # Pass the student's profile
        'active_tab': 'chats',
        'total_unread': total_unread,
        'search_query': query,
        'online_user_ids': _get_online_user_ids(),
    }
    return render(request, 'Chat/student_chat_list.html', context)
