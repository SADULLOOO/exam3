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

def login_user(request):
    if request.method=='POST':
        password = request.POST.get('password')
        username = request.POST.get('username')
        email = request.POST.get('username')

        user = authenticate(
            password=password,
            username=username,
            email=email
        )

        if not user:
            not_active = User.objects.filter(username=username, is_active=False).first()
            if not_active:
                return render(request, 'accounts/login.html', {'error': 'Go and confirm your email'})
            else:
                return render(request, 'accounts/login.html', {'error': 'Username or password isnt correct'})
            
        else:
            login(request, user)
            return redirect('/')
        
    else:
        return render(request, 'accounts/login.html')
    
def logout_user(request):
    logout(request)
    return redirect('login_user')


def confirm_email(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        code = request.POST.get('code')

        user = User.objects.filter(username=username).first()

        if not user:
            return render(request, 'accounts/confirm_email.html', {'error': 'Invalid username!'})
        if user.is_active:
            return redirect('login_user')
        confirm = EmailConfirm.objects.filter(user=user, code=code).first()

        if not confirm:
            return render(request, 'accounts/confirm_email.html', {'error': 'Invalid input code!'})
        user.is_active=True
        user.save()
        return redirect('login_user') 
    else:
        return render(request, 'accounts/confirm_password.html')
    
   
def send_reset_password(user):
    code = randint(100000, 999999)
    PasswordReset.objects.update_or_create(
        user=user,
        defaults={'code': code}
    )

    send_mail(
        subject='Reset Password',
        message=f'Your reset code is: {code}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False
    )
