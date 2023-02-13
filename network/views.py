from sqlite3 import Timestamp
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.paginator import Paginator
import json

from .models import User, Post, Follower

POST_PER_PAGE = 10

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


def index(request):

    postData = Post.objects.all().order_by('-timestamp')
    paginator = Paginator(postData, POST_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.user.is_authenticated:
        currentuser = User.objects.get(id=request.session['_auth_user_id'])

        paginator = Paginator(postData, POST_PER_PAGE)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, "network/index.html", {
            "postData": page_obj,
            "loginUser": currentuser
        })

    return render(request, "network/index.html", {
        "postData": page_obj,
    })

@csrf_exempt
def editpost(request):
    if request.method == "POST":
        post_id = request.POST.get("id")
        new_post = request.POST.get("post")
        try:
            post = Post.objects.get(id=post_id)
            if post.user == request.user:
                post.content = new_post.strip()
                post.save()
                return JsonResponse({}, status=201)
        except:
            return JsonResponse({}, status=404)

    return JsonResponse({}, status=400)
    
@csrf_exempt
def like(request):
    if request.method == "POST":
        post_id = request.POST.get("id")
        liked = request.POST.get("liked")
        try:
            post = Post.objects.get(id=post_id)
            if liked == "no":
                post.like.add(request.user)
                liked = "yes"
            elif liked == "yes":
                post.like.remove(request.user)
                liked = "no"
            post.save()
            return JsonResponse({"like_count":post.like.count(), "liked": liked , "status":201})
        except:
            return JsonResponse({"error":"Cant Find Post", "status":404})
    return JsonResponse({}, status=400)



def post(request):
    if request.method == "POST":
        content = request.POST["content"]
        currentUser = request.user
        newpost = Post(
            user=currentUser,
            content=content
        )
        newpost.save()
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request,"network/index.html")


def follow(request, id):
    try: 
        result = "follow"
        currentuser = User.objects.get(id=request.session['_auth_user_id'])
        user_page = User.objects.get(pk=id)
        follower = Follower.objects.get_or_create(follower=currentuser, following=user_page)
        if not follower[1]:
            Follower.objects.filter(follower=currentuser, following=user_page).delete()
            result = "unfollow"
        total_followers = Follower.objects.filter(following=user_page).count()
    except KeyError:
        return HttpResponseBadRequest("Bad Request Try Again!")
    return JsonResponse({"result": result, "total_followers": total_followers})


def profile(request, username):
    is_following = 0
    
    userinfo = User.objects.get(username=username)
    if request.user.is_authenticated:
        currentuser = request.session['_auth_user_id']
        is_following = Follower.objects.filter(follower=currentuser, following=userinfo).count()
        postData = Post.objects.filter(user=userinfo.id).order_by('-timestamp')
    else:
        postData = Post.objects.filter(username=userinfo.id).order_by('-timestamp')

    total_following = Follower.objects.filter(follower=userinfo).count()
    total_followers = Follower.objects.filter(following=userinfo).count()

    # Paginator page 
    paginator = Paginator(postData, POST_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/profile.html",{
        "postData" : page_obj,
        "userinfo" : userinfo,
        "total_following" : total_following, 
        "total_followers" : total_followers,
        "is_following" : is_following
    })

def following(request):
    if request.user.is_authenticated:
        currentuser = request.session['_auth_user_id']
        followeduser = Follower.objects.filter(follower=currentuser)
        postData = Post.objects.filter(user_id__in=followeduser.values("following_id")).order_by('-timestamp')
    else:
        return HttpResponseRedirect(reverse("login"))
    
        # Paginator page 
    paginator = Paginator(postData, POST_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "network/following.html",{
        "postData": page_obj
    })



