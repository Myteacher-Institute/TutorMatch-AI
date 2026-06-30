from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('chat/<int:booking_id>/', views.chat_view, name='chat_view'),
    path('chat/<int:booking_id>/send/', views.send_message, name='send_message'),
    path('tutor/chats/', views.tutor_chat_list, name='tutor_chat_list'),
    path('student/chats/', views.student_chat_list, name='student_chat_list'),
    path('chat-admin/chats/', views.admin_chat_list, name='admin_chat_list'),
    path('chat/<int:booking_id>/messages/<int:last_message_id>/', views.get_new_messages, name='get_new_messages'),
]
