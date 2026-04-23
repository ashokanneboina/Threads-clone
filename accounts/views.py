from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from accounts.models import CustomUser, Profile, Follows, Thread, Like, Saved, Notification, Comment
from .forms import LoginForm, SignupForm
from django.contrib.auth.decorators import login_required


from django.utils.timesince import timesince

import base64

# Create your views here.



def login_view(request):
    form = LoginForm()
    error = None

    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            user = authenticate(request, username=username, password=password)

            if user:
                login(request, user)
                return redirect("/")
            else:
                error = "Invalid username or password"

    return render(request, "login.html", {"form": form, "error": error})


@login_required
def logout_view(request):
    logout(request)
    return redirect("login")


def signup_view(request):
    form = SignupForm()
    error = ""
    if request.method == "POST":
        form = SignupForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            email = form.cleaned_data["email"]
            if CustomUser.objects.filter(username=username).exists():
                form.add_error("username", "Username already taken")

           
            elif CustomUser.objects.filter(email=email).exists():
                form.add_error("email", "Email already registered")

            else:
                user = CustomUser.objects.create_user(
                    username=username, password=password, email=email
                )
    
                login(request, user)
                return redirect("/")
    return render(request, "signup.html", {
        "form": form,
        "error": error
    })


@login_required
def profile_view(request):
    user = request.user
    profile = user.profile

    profile_image = None
    if profile.profile_pic:
        import base64

        profile_image = base64.b64encode(profile.profile_pic).decode("utf-8")

    followers_count = Follows.objects.filter(following_id=user).count()

    following_count = Follows.objects.filter(follower_id=user).count()

    context = {
        "username": user.username,
        "profile_image": profile_image,
        "bio": profile.bio,
        "followers_count": followers_count,
        "following_count": following_count,
    }

    return render(request, "profile.html", context)


def search_view(request):
    query = request.GET.get("q")
    users_list = CustomUser.objects.all()
    if request.user.is_authenticated:
        users_list = users_list.exclude(id=request.user.id)
    if query:
        users_list = users_list.filter(username__icontains=query)

    users_with_info = []

    for user in users_list:
        profile = user.profile
        profile_image = None

        if profile.profile_pic:
            profile_image = base64.b64encode(profile.profile_pic).decode("utf-8")

        is_following = Follows.objects.filter(
            follower_id=request.user.id, following_id=user.id
        ).exists()
        users_with_info.append(
            {
                "username": user.username,
                "id": user.id,
                "profile_image": profile_image,
                "bio": user.profile.bio,
                "is_following": is_following,
            }
        )
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return render(request, "partials/user_list.html", {"users": users_with_info})
    return render(request, "search.html", {"users": users_with_info})

@login_required
def activity_view(request):

    notifications = Notification.objects.filter(
        receiver=request.user
    ).select_related('sender', 'sender__profile', 'thread').order_by('-created_at')


    following_users = set(
        Follows.objects.filter(follower_id=request.user)
        .values_list('following_id', flat=True)
    )

    activity_data = []

    for n in notifications:


        is_following = n.sender.id in following_users


        profile_pic = None
        if hasattr(n.sender, 'profile') and n.sender.profile.profile_pic:
            profile_pic = base64.b64encode(
                n.sender.profile.profile_pic
            ).decode('utf-8')

        activity_data.append({
            "id": n.id,
            "type": n.notification_type,
            "sender_username": n.sender.username,
            "sender_id": n.sender.id,
            "profile_pic": profile_pic, 
            "thread_id": n.thread.id if n.thread else None,
            "is_read": n.is_read,
            "time": n.created_at,
            "is_following": is_following,
        })


    notifications.filter(is_read=False).update(is_read=True)

    return render(request, 'activity.html', {
        'notifications': activity_data
    })


def feed_view(request):
    threads = Thread.objects.all().order_by("-created_at")

    threads_data = []

    for t in threads:
        profile = t.user.profile

        profile_image = None
        if profile.profile_pic:
            profile_image = base64.b64encode(profile.profile_pic).decode("utf-8")

        thread_image = None
        if t.image:
            thread_image = base64.b64encode(t.image).decode("utf-8")

        threads_data.append(
            {
                "username": t.user.username,
                "profile_image": profile_image,
                "content": t.content,
                "image": thread_image,
                "created_at": timesince(t.created_at) + " ago",
                "likes_count": t.likes.count(),
                "id": t.id,
                "is_liked": (
                    Like.objects.filter(user=request.user, thread=t).exists()
                    if request.user.is_authenticated
                    else False
                ),
                "is_saved": (
                    Saved.objects.filter(user=request.user, thread=t).exists()
                    if request.user.is_authenticated
                    else False
                ),
                "comments_count": t.comments.count(),
            }
        )

    return render(request, "feed.html", {"threads": threads_data})



@login_required
def saved_view(request):

    saved_threads = Thread.objects.filter(saved__user=request.user).order_by(
        "-created_at"
    )

    threads_data = []

    for t in saved_threads:
        profile = t.user.profile

        profile_image = None
        if profile.profile_pic:
            profile_image = base64.b64encode(profile.profile_pic).decode("utf-8")

        thread_image = None
        if t.image:
            thread_image = base64.b64encode(t.image).decode("utf-8")

        threads_data.append(
            {
                "username": t.user.username,
                "profile_image": profile_image,
                "content": t.content,
                "image": thread_image,
                "created_at": timesince(t.created_at) + " ago",
                "likes_count": t.likes.count(),
                "id": t.id,
                "is_liked": Like.objects.filter(user=request.user, thread=t).exists(),
                "is_saved": True,  # always true in saved page
            }
        )

    return render(request, "saved.html", {"threads": threads_data})

@login_required
def edit_view(request):
    profile = Profile.objects.get(user=request.user)
    profile_image = None
    if request.method == "POST":
        username = request.POST.get("editUserName")
        image = request.FILES.get("profile_image")
        bio = request.POST.get("bio")

        if username:
            request.user.username = username
            request.user.save()
        if image:
            profile.profile_pic = image.read()

        if bio:
            profile.bio = bio

        profile.save()

        return redirect("profile")
    if profile.profile_pic:
        profile_image = base64.b64encode(profile.profile_pic).decode("utf-8")
    return render(
        request, "edit_profile.html", {"profile": profile, "profile_pic": profile_image}
    )


@login_required
def follow_user(request):
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        user_to_follow = get_object_or_404(CustomUser, id=user_id)
        if request.user == user_to_follow:
            return JsonResponse({"error": "cannot follow yourself"}, status=400)
        follow = Follows.objects.filter(
            follower_id=request.user, following_id=user_to_follow
        )
        if follow.exists():
            follow.delete()
            return JsonResponse({"status": "unfollowed"})
        else:
            Follows.objects.create(
                follower_id=request.user, following_id=user_to_follow
            )
            Notification.objects.create(
                sender=request.user,
                receiver=user_to_follow,
                notification_type='follow'
            )
            return JsonResponse({"status": "followed"})


@login_required
def create_thread(request):
    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        image = request.FILES.get("image")

        image_data = image.read() if image else None

        if content or image_data:
            Thread.objects.create(user=request.user, content=content, image=image_data)
            return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error"})




@login_required
def toggle_like(request, thread_id):
    if request.method == "POST":
        thread = Thread.objects.get(id=thread_id)

        like, created = Like.objects.get_or_create(
            user=request.user,
            thread=thread
        )

        if not created:
            like.delete()

            Notification.objects.filter(
                sender=request.user,
                receiver=thread.user,
                notification_type='like',
                thread=thread
            ).delete()

            return JsonResponse({
                "status": "unliked",
                "likes_count": thread.likes.count()
            })

        if thread.user != request.user:   
            Notification.objects.create(
                sender=request.user,
                receiver=thread.user,
                notification_type='like',
                thread=thread
            )

        return JsonResponse({
            "status": "liked",
            "likes_count": thread.likes.count()
        })

    return JsonResponse({"status": "error"})

@login_required
def toggle_save(request, thread_id):
    if request.method == "POST":
        thread = Thread.objects.get(id=thread_id)

        saved, created = Saved.objects.get_or_create(user=request.user, thread=thread)

        if not created:
            saved.delete()
            return JsonResponse({"status": "unsaved"})

        return JsonResponse({"status": "saved"})

    return JsonResponse({"status": "error"})



@login_required
def thread_detail(request, thread_id):
    thread = Thread.objects.get(id=thread_id)

    profile_image = None
    thread_image = None

    if thread.user.profile.profile_pic:
        profile_image = base64.b64encode(
            thread.user.profile.profile_pic
        ).decode("utf-8")

    if thread.image:
        thread_image = base64.b64encode(
            thread.image
        ).decode("utf-8")

    comments = Comment.objects.filter(
        thread=thread,
        parent__isnull=True
    ).select_related('user').prefetch_related('replies')

    return render(request, "thread_detail.html", {
        "thread": thread,
        "profile_image": profile_image,
        "thread_image": thread_image,   # ✅ FIXED
        "comments": comments
    })

@login_required
def create_comment(request, thread_id):
    if request.method == "POST":
        content = request.POST.get("content")
        parent_id = request.POST.get("parent_id")

        thread = Thread.objects.get(id=thread_id)

        parent = None
        if parent_id:
            parent = Comment.objects.get(id=parent_id)

        Comment.objects.create(
            user=request.user,
            thread=thread,
            parent=parent,
            content=content
        )

        return JsonResponse({"status": "success"})

    return JsonResponse({"status": "error"})