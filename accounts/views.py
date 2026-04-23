from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from accounts.models import CustomUser, Profile, Follows, Thread, Like, Saved, Notification, Comment, Conversation, Message
from .forms import LoginForm, SignupForm
from django.contrib.auth.decorators import login_required


from django.utils.timesince import timesince
from django.db.models import Count

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
    active_tab = request.GET.get("tab", "threads")
    if active_tab not in {"threads", "replies"}:
        active_tab = "threads"

    profile_image = None
    if profile.profile_pic:
        import base64

        profile_image = base64.b64encode(profile.profile_pic).decode("utf-8")

    followers_count = Follows.objects.filter(following_id=user).count()

    following_count = Follows.objects.filter(follower_id=user).count()

    threads_data = []
    replies_data = []

    if active_tab == "threads":
        threads = list(
            Thread.objects.filter(user=user)
            .annotate(
                likes_count=Count("likes", distinct=True),
                comments_count=Count("comments", distinct=True),
            )
            .order_by("-created_at")
        )

        thread_ids = [t.id for t in threads]
        liked_ids = set(
            Like.objects.filter(user=request.user, thread_id__in=thread_ids).values_list(
                "thread_id", flat=True
            )
        )
        saved_ids = set(
            Saved.objects.filter(
                user=request.user, thread_id__in=thread_ids
            ).values_list("thread_id", flat=True)
        )

        for t in threads:
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
                    "likes_count": t.likes_count,
                    "id": t.id,
                    "is_liked": t.id in liked_ids,
                    "is_saved": t.id in saved_ids,
                    "comments_count": t.comments_count,
                }
            )
    else:
        replies = (
            Comment.objects.filter(user=user)
            .select_related("thread", "thread__user", "thread__user__profile")
            .order_by("-created_at")
        )

        for c in replies:
            thread_profile_image = None
            if c.thread.user.profile.profile_pic:
                thread_profile_image = base64.b64encode(
                    c.thread.user.profile.profile_pic
                ).decode("utf-8")

            replies_data.append(
                {
                    "id": c.id,
                    "content": c.content,
                    "created_at": timesince(c.created_at) + " ago",
                    "thread_id": c.thread.id,
                    "thread_content": c.thread.content,
                    "thread_username": c.thread.user.username,
                    "thread_profile_image": thread_profile_image,
                }
            )

    context = {
        "username": user.username,
        "profile_image": profile_image,
        "bio": profile.bio,
        "followers_count": followers_count,
        "following_count": following_count,
        "active_tab": active_tab,
        "threads": threads_data,
        "replies": replies_data,
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
def delete_thread(request, thread_id):
    if request.method != "POST":
        return JsonResponse({"status": "error"}, status=405)

    thread = get_object_or_404(Thread, id=thread_id, user=request.user)
    thread.delete()

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"status": "success"})

    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or "/profile/"
    return redirect(next_url)




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


@login_required
def chat_list_view(request):
    conversations = Conversation.objects.filter(participants=request.user).prefetch_related('messages', 'participants')

    conversations_data = []

    for conv in conversations:
        other_participants = conv.participants.exclude(id=request.user.id)
        if other_participants.exists():
            other_user = other_participants.first()
            last_message = conv.messages.last()

            profile_image = None
            if other_user.profile.profile_pic:
                profile_image = base64.b64encode(other_user.profile.profile_pic).decode('utf-8')

            conversations_data.append({
                'id': conv.id,
                'other_username': other_user.username,
                'other_profile_image': profile_image,
                'last_message': last_message.content if last_message else '',
                'last_message_time': last_message.created_at if last_message else None,
            })

    # Get mutual followers
    following_ids = Follows.objects.filter(follower_id=request.user).values_list('following_id', flat=True)
    followers_ids = Follows.objects.filter(following_id=request.user).values_list('follower_id', flat=True)
    mutual_ids = set(following_ids) & set(followers_ids)

    users = CustomUser.objects.filter(id__in=mutual_ids).exclude(id=request.user.id)

    users_data = []
    for user in users:
        profile_image = None
        if user.profile.profile_pic:
            profile_image = base64.b64encode(user.profile.profile_pic).decode('utf-8')

        users_data.append({
            'id': user.id,
            'username': user.username,
            'profile_image': profile_image,
            'bio': user.profile.bio,
        })

    return render(request, 'chat_list.html', {'conversations': conversations_data, 'users': users_data})


@login_required
def chat_detail_view(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)

    other_participants = conversation.participants.exclude(id=request.user.id)
    other_user = other_participants.first()

    other_profile_image = None
    if other_user.profile.profile_pic:
        other_profile_image = base64.b64encode(other_user.profile.profile_pic).decode('utf-8')

    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(conversation=conversation, sender=request.user, content=content)
            return redirect('chat_detail', conversation_id=conversation.id)

    messages = conversation.messages.select_related('sender')

    messages_data = []
    for msg in messages:
        messages_data.append({
            'sender_username': msg.sender.username,
            'content': msg.content,
            'created_at': msg.created_at,
            'is_own': msg.sender == request.user,
        })

    return render(request, 'chat_detail.html', {
        'messages': messages_data,
        'other_username': other_user.username,
        'other_profile_image': other_profile_image,
    })


@login_required
def start_chat_view(request, user_id):
    other_user = get_object_or_404(CustomUser, id=user_id)

    # Check if mutual follow
    is_following = Follows.objects.filter(follower_id=request.user, following_id=other_user).exists()
    is_followed_by = Follows.objects.filter(follower_id=other_user, following_id=request.user).exists()

    if not (is_following and is_followed_by):
        return redirect('chat_list')

    # Get or create conversation
    conversation = Conversation.objects.filter(participants=request.user).filter(participants=other_user).first()

    if not conversation:
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user, other_user)

    return redirect('chat_detail', conversation_id=conversation.id)
