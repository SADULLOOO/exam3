from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from .models import Profile
from .forms import ProfileForm
from cars.models import Favorite, Review, UserActivity, Credit, Order, Brand
from django.http import JsonResponse
import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
from django.http import HttpResponseForbidden
from .models import Profile, License
from .forms import LicenseApplicationForm
from cars.models import Brand, CarModel, Car, AIChatHistory, UserActivity
@login_required
def update_profile(request):

    profile, created = Profile.objects.get_or_create(
        user=request.user
    )

    form = ProfileForm(
        request.POST or None,
        request.FILES or None,
        instance=profile
    )

    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect('profile')

    return render(request, 'profiles/update_profile.html', {
        'form': form,
        'profile': profile
    })

@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    favorites = Favorite.objects.filter(user=request.user)
    reviews = Review.objects.filter(user=request.user)
    orders = Order.objects.filter(user=request.user)
    credits = Credit.objects.filter(user=request.user)

    activity, created = UserActivity.objects.get_or_create(user=request.user)
    live_seconds = activity.total_seconds

    context = {
        'profile': profile,
        'favorites': favorites,
        'reviews': reviews,
        'orders': orders,
        'credits': credits,
        'live_seconds': live_seconds,
    }

    if request.user.is_superuser:
        context['deleted_brands'] = Brand.all_objects.filter(is_deleted=True)

    return render(request, 'profiles/profile.html', context)


@login_required
def request_license_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if hasattr(request.user, 'license') and request.user.license.is_active:
        return redirect('profile')

    if request.method == "POST":
        form = LicenseApplicationForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            with transaction.atomic():
                instance = form.save(commit=False)
                instance.applied_for_license = True
                instance.save()

                unique_key = f"CARORDER-PRO-{uuid.uuid4().hex[:12].upper()}"
                
                license_obj, created = License.objects.get_or_create(
                    user=request.user,
                    defaults={
                        'license_key': unique_key,
                        'is_active': True, 
                        'price_per_month': 15000.00
                    }
                )
                if not created:
                    license_obj.is_active = True
                    license_obj.save()

                default_brand = Brand.objects.create(
                    owner=request.user,
                    name=f"Brand of {request.user.username}"
                )

                default_model = CarModel.objects.create(
                    brand=default_brand,
                    name="Starter Model"
                )

                Car.objects.create(
                    model=default_model,
                    owner=request.user,
                    title="My First Demo Car",
                    price=25000.00,
                    year=2025,
                    mileage=0,
                    engine="Electric",
                    engine_volume=0.0,
                    horsepower=300,
                    color="Black",
                    country="USA",
                    transmission="automatic",
                    fuel_type="electric",
                    status="new",
                    description="This is your first auto-generated car. You can update or delete it!"
                )

                AIChatHistory.objects.create(
                    user=request.user,
                    user_message="SYSTEM INITIALIZATION",
                    ai_response=f"Привет, {request.user.username}! Твоя система CarOrder готова к работе. 🚀 Напиши мне, чтобы настроить продажи!"
                )

                messages.success(request, f"Поздравляем! Ваша лицензия {unique_key} успешно активирована!")
                return redirect('license_success')
    else:
        form = LicenseApplicationForm(instance=profile)

    return render(request, 'profiles/request_license.html', {'form': form})

@login_required
def license_success_view(request):
    lic = get_object_or_404(License, user=request.user)
    return render(request, 'profiles/license_certificate.html', {'license': lic})



@login_required
def superuser_dashboard_view(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Вы не босс платформы!")

    licenses = License.objects.select_related('user').all()
    
    dashboard_data = []
    for lic in licenses:
        current_price = lic.check_and_update_price()
        
        activity = UserActivity.objects.filter(user=lic.user).first()
        
        from django.utils.timezone import now
        if activity and activity.last_seen:
            is_sleeping = (now() - activity.last_seen).total_seconds() > 900 
        else:
            is_sleeping = True

        dashboard_data.append({
            'license': lic,
            'current_price': current_price,
            'activity': activity,
            'status': "💤 Спит / АФК" if is_sleeping else "🔥 Работает!",
        })

    return render(request, 'profiles/superuser_dashboard.html', {'data': dashboard_data})


@login_required
def toggle_license_status(request, license_id):
    """Кнопка Kill-Switch: Босс может в любое время отключить лицензию"""
    if not request.user.is_superuser:
        return HttpResponseForbidden()
        
    lic = get_object_or_404(License, id=license_id)
    lic.is_active = not lic.is_active
    lic.save()
    
    messages.info(request, f"Status {lic.user.username} changed on: {lic.is_active}")
    return redirect('superuser_dashboard')