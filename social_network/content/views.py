from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def post(request, post_id):
    return HttpResponse(f"You're looking at post {post_id}")

def hello_user(request, username):
    return HttpResponse(f"Hello, {username.capitalize()}!")
