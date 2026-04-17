
from django.urls import path

from .views import follow_user, insights_view, login_view, logout_view, signup_view, profile_view, search_view, feed_view
from .views import activity_view, saved_view, edit_view, create_thread, toggle_like,  toggle_save


urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('signup/', signup_view, name='signup'),

    path('profile/', profile_view, name='profile'),
    path('search/', search_view, name='search'),
    path('', feed_view, name='feed'),
    path('activity/', activity_view, name='activity'),
    path('insights/', insights_view, name='insights'),
    path('saved/', saved_view, name='saved'),
    path('edit/', edit_view, name='edit'),
    
    path('follow_user/', follow_user, name='follow_user'),
    path('create-thread/', create_thread),
    path('like/<int:thread_id>/', toggle_like),
    path('save/<int:thread_id>/', toggle_save),
    
]

