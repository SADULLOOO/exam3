from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth import authenticate, login, logout
from random import randint
from .models import EmailConfirm, User, PasswordReset
from django.core.mail import send_mail
from django.conf import settings
from myprofile.models import Profile

def send_confirmation_email(user):
    code = randint(100000, 999999)
    EmailConfirm.objects.update_or_create(user=user, defaults={'code': code})
    try:
        send_mail(
            subject='Confirm your email!',
            message=f'Hello mr/s {user.username} welcome to our safely web application please confirm your code: {code}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email]
        )

    except Exception as e:
        print(e, '==========================+++++++++++++++++++++++==========================')

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        age = request.POST.get('age')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if not username or not email or not password1 or not age or not phone:
            return render(request, 'accounts/register.html', {'error': 'All info are required'})

        if password1 != password2:
            return render(request, 'accounts/register.html', {'error': 'Password doesnt match'})

        if User.objects.filter(username=username).exists():
            return render(request, 'accounts/register.html', {'error': 'Username already exists'})

        if User.objects.filter(email=email).exists():
            return render(request, 'accounts/register.html', {'error': 'Email already exists'})

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            age=age,
            phone=phone
        )

        user.is_active = False
        user.save()

        Profile.objects.get_or_create(user=user)

        send_confirmation_email(user)

        return render(request, 'accounts/confirm_password.html', {'username': user.username})

    else:
        return render(request, 'accounts/register.html')


   