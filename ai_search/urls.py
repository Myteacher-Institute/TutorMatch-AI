from django.urls import path

from . import views

urlpatterns = [
    path("find-tutor/", views.find_tutor, name="find_tutor"),
    path("ai-assistant/", views.ai_assistant, name="ai_assistant"),
    path("delete-conversation/<int:conversation_id>/", views.delete_conversation, name="delete_conversation"),
    path("search-results/", views.search_results, name="search_results"),
]
