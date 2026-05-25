from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Profile
from .forms import ProfileForm


@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    return render(request, 'profiles/profile.html', {'profile': profile})


@login_required
def update_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

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