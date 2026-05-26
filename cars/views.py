from django.shortcuts import render, get_object_or_404
from .models import Brand, CarModel, Car


def home(request):

    brands = Brand.objects.all()

    recommended_cars = Car.objects.all().order_by('-created_at')[:6]

    return render(request, 'cars/home.html', {
        'brands': brands,
        'recommended_cars': recommended_cars
    })

