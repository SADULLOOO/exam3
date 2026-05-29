from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from .models import Brand, CarModel, Car, CarImage, Favorite, Review, OrderRequest, Order, Credit, UserActivity, Message, Conversation
from .filters import CarFilter
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.signals import user_logged_in
from django.utils.timezone import now
from django.contrib.auth.signals import user_logged_out
from django.http import JsonResponse
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from .models import UserActivity
from groq import Groq
from dotenv import load_dotenv
import os
from django.contrib.auth import get_user_model
from .models import Conversation, Message, Car
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CarForm, CarImageForm
User = get_user_model()
from django.http import HttpResponseForbidden
load_dotenv()
groq_api = os.getenv("GROQ_API_KEY")


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

    if request.method == 'POST':

        if request.user.is_authenticated:

            text = request.POST.get('text')

            stars = request.POST.get('stars')

            Review.objects.create(
                user=request.user,
                car=car,
                text=text,
                stars=stars
            )

            return redirect(
                'car_detail',
                car_id=car.id
            )

    related_cars = Car.objects.filter(
        model=car.model
    ).exclude(id=car.id)[:4]

    is_favorite = False

    if request.user.is_authenticated:

        is_favorite = Favorite.objects.filter(
            user=request.user,
            car=car
        ).exists()

    return render(request, 'cars/car_detail.html', {
        'car': car,
        'related_cars': related_cars,
        'is_favorite': is_favorite
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


@login_required
def add_favorite(request, car_id):

    car = get_object_or_404(
        Car,
        id=car_id
    )

    favorite = Favorite.objects.filter(
        user=request.user,
        car=car
    )

    if favorite.exists():

        favorite.delete()

    else:

        Favorite.objects.create(
            user=request.user,
            car=car
        )

    return redirect(
        'car_detail',
        car_id=car.id
    )

@login_required
def buy_car(request, car_id):

    car = get_object_or_404(Car, id=car_id)

    Order.objects.create(
        user=request.user,
        car=car
    )

    return redirect('profile')


@login_required
def take_credit(request, car_id):

    car = get_object_or_404(Car, id=car_id)

    Credit.objects.create(
        user=request.user,
        car=car,
        amount=car.price,
        months=12
    )

    return redirect('profile')



@login_required
def heartbeat(request):
    activity, created = UserActivity.objects.get_or_create(user=request.user)
    current_time = now()

    if activity.last_seen:
        delta = (current_time - activity.last_seen).total_seconds()
        
        if delta < 15:
            activity.total_seconds += int(delta)
    
    activity.last_seen = current_time
    activity.save()

    return JsonResponse({"status": "ok"})



@login_required
def get_live_time(request):
    activity, created = UserActivity.objects.get_or_create(user=request.user)
    
    return JsonResponse({"seconds": activity.total_seconds})


@login_required
def cancel_order(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    order.status='cancelled'

    order.save()

    return redirect('profile')

@login_required
def cancel_credit(request, credit_id):

    credit=get_object_or_404(
        Credit,
        id=credit_id,
        user=request.user
    )

    credit.status='cancelled'

    credit.save()

    return redirect('profile')

def about(request):

    return render(
        request,
        'cars/about.html'
    )


def ai_help(request):

    answer = ""

    prompt = request.GET.get(
        'prompt',
        ''
    ).strip()

    if prompt:

        client = Groq(
            api_key=groq_api
        )

        cars = Car.objects.select_related(
            'model'
        )

        cars_for_ai = []

        for car in cars:

            cars_for_ai.append({

                'name': car.title,

                'price': car.price,

                'brand': car.model.brand.name,

                'model': car.model.name

            })

        system_prompt = f"""

You are OrderCar AI assistant.

Help users choose cars.

Recommend ONLY from this list:

{cars_for_ai}

Speak friendly.

Explain simply.

"""

        response = client.chat.completions.create(

            model="openai/gpt-oss-120b",

            messages=[

                {
                    "role":"system",
                    "content":system_prompt
                },

                {
                    "role":"user",
                    "content":prompt
                }

            ]

        )

        answer = response.choices[0].message.content

    return render(
        request,
        'cars/ai_help.html',
        {
            'answer': answer,
            'prompt': prompt
        }
    )


@login_required
def chat_owner(request, car_id=None):
    if request.user.is_superuser:
        return redirect("chat_admin_list")

    car = get_object_or_404(Car, id=car_id)
    
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        return render(request, "chat/chat.html", {"error": "Not admin yet."})

    conversation, created = Conversation.objects.get_or_create(
        car=car,
        buyer=request.user,
        owner=admin_user
    )

    if request.method == "POST":
        text = request.POST.get("message")
        if text:
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                text=text
            )
        return redirect("chat_owner", car_id=car.id)

    messages = conversation.messages.order_by("id")
    return render(request, "chat/chat.html", {
        "car": car,
        "messages": messages,
        "conversation": conversation
    })


@login_required
def admin_chat_view(request, chat_id=None):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Permission gave only to admin.")

    if not chat_id:
        all_chats = Conversation.objects.all().select_related('buyer', 'car')
        return render(request, "chat/admin_list.html", {"conversations": all_chats})
    
    conversation = get_object_or_404(Conversation, id=chat_id)
    car = conversation.car

    if request.method == "POST":
        text = request.POST.get("message")
        if text:
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                text=text
            )
        return redirect("chat_owner_admin", chat_id=conversation.id)

    messages = conversation.messages.order_by("id")
    return render(request, "chat/chat.html", {
        "car": car,
        "messages": messages,
        "conversation": conversation
    })

@staff_member_required
def add_car(request):
    if request.method == "POST":
        form = CarForm(request.POST, request.FILES)

        if form.is_valid():
            car = form.save()

            images = request.FILES.getlist('images')
            for img in images:
                CarImage.objects.create(car=car, image=img)

            return redirect('home')
    else:
        form = CarForm()

    return render(request, "cars/add_car.html", {
        "form": form
    })

@staff_member_required
def delete_car(request, car_id):
    car = get_object_or_404(Car, id=car_id)

    if request.method == "POST":
        car.delete()
        return redirect("home")

    return render(request, "cars/delete.html", {
        "car": car
    })

@staff_member_required
def edit_car(request, car_id):
    car = get_object_or_404(Car, id=car_id)

    form = CarForm(request.POST or None, instance=car)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("car_detail", car_id=car.id)

    return render(request, "cars/edit_car.html", {
        "form": form,
        "car": car
    })