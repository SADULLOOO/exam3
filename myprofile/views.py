from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from .models import Profile
from .forms import ProfileForm
from cars.models import Favorite, Review, UserActivity, Credit, Order
from django.http import JsonResponse

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

    activity, created = UserActivity.objects.get_or_create(user=request.user)

    live_seconds = activity.total_seconds

    if activity.last_seen:
        live_seconds = activity.total_seconds
    else:
        live_seconds = 0

    orders = Order.objects.filter(
    user=request.user
    )

    credits = Credit.objects.filter(
    user=request.user
    )

    return render(request, 'profiles/profile.html', {
        'profile': profile,
        'favorites': favorites,
        'reviews': reviews,
        'orders': orders,
        'credits': credits,
        'live_seconds': live_seconds
    })
    




