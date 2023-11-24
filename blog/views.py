from django.shortcuts import render
from django.http import HttpResponse
from .models import Post
import logging

logger = logging.getLogger(__name__)

def blog1(request):
    logger.info("blog1 page called")
    return render(request, 'blog/blog.html', {})

def firstblog(request):
    logger.info("firstblog page called")
    return render(request, 'blog/firstblog.html', {})

def post_list(request):
    posts = Post.objects.all()
    return render(request, 'blog/post_list.html', {'posts': posts})


