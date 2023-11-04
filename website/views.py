from django.shortcuts import render

def home(request):
    return render(request, 'home.html', {})


def vision(request):
    return render(request, 'vision.html', {})