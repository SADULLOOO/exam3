from django.shortcuts import render, get_object_or_404
from .models import Brand, CarModel, Car
from .filters import CarFilter
from django.db.models import Q

def brand_detail(request, brand_id):

    brand = get_object_or_404(
        Brand,
        id=brand_id
    )

    models = CarModel.objects.filter(
        brand=brand
    )

    return render(request, 'cars/brand_detail.html', {
        'brand': brand,
        'models': models
    })


def model_detail(request, model_id):

    model = get_object_or_404(
        CarModel,
        id=model_id
    )

    cars = Car.objects.filter(
        model=model
    )

    status = request.GET.get('status')
    fuel = request.GET.get('fuel')
    transmission = request.GET.get('transmission')

    if status:
        cars = cars.filter(status=status)

    if fuel:
        cars = cars.filter(fuel_type=fuel)

    if transmission:
        cars = cars.filter(
            transmission=transmission
        )

    return render(request, 'cars/model_detail.html', {
        'model': model,
        'cars': cars
    })

def car_detail(request, car_id):

    car = get_object_or_404(
        Car,
        id=car_id
    )

    related_cars = Car.objects.filter(
        model=car.model
    ).exclude(id=car.id)[:4]

    return render(request, 'cars/car_detail.html', {
        'car': car,
        'related_cars': related_cars
    })


def home(request):

    brands = Brand.objects.all()

    recommended_cars = Car.objects.all().order_by('-created_at')[:8]

    return render(request, 'cars/home.html', {
        'brands': brands,
        'recommended_cars': recommended_cars,
    })


def search(request):

    query = request.GET.get('q', '')

    cars = Car.objects.all()

    if query:

        cars = cars.filter(
            Q(title__icontains=query) |
            Q(model__name__icontains=query) |
            Q(model__brand__name__icontains=query) |
            Q(engine__icontains=query) |
            Q(country__icontains=query) |
            Q(description__icontains=query)
        ).distinct()

    car_filter = CarFilter(request.GET, queryset=cars)

    return render(request, 'cars/search.html', {
        'filter': car_filter,
        'cars': car_filter.qs,
        'query': query,
    })
