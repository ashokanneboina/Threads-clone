from django.urls import path

from .views import (
    follow_user,
    login_view,
    logout_view,
    signup_view,
    profile_view,
    search_view,
    feed_view,
)
from .views import (
    activity_view,
    chat_detail_view,
    chat_list_view,
    saved_view,
    edit_view,
    create_thread,
    start_chat_view,
    toggle_like,
    toggle_save,
    thread_detail,
    create_comment,
    delete_thread,
)

urlpatterns = [
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("signup/", signup_view, name="signup"),
    path("profile/", profile_view, name="profile"),
    path("search/", search_view, name="search"),
    path("", feed_view, name="feed"),
    path("chat/", chat_list_view, name="chat_list"),
    path("chat/start/<uuid:user_id>/", start_chat_view, name="start_chat"),
    path("chat/<uuid:conversation_id>/", chat_detail_view, name="chat_detail"),
    path("activity/", activity_view, name="activity"),
    path("saved/", saved_view, name="saved"),
    path("edit/", edit_view, name="edit"),
    path("follow_user/", follow_user, name="follow_user"),
    path("create-thread/", create_thread),
    path("like/<int:thread_id>/", toggle_like),
    path("save/<int:thread_id>/", toggle_save),
    # urls.py
    path("thread/<int:thread_id>/", thread_detail, name="thread_detail"),
    path("thread/<int:thread_id>/comment/", create_comment, name="create_comment"),
    path("thread/<int:thread_id>/delete/", delete_thread, name="delete_thread"),
]
