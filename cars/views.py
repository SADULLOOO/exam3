from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from .models import Brand, CarModel, Car, CarImage, Favorite, Review, Order, Credit, UserActivity, Message, Conversation, AIChatHistory
from .filters import CarFilter
from django.db.models import Q, Count
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
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
from .forms import CarForm
User = get_user_model()
from django.http import HttpResponseForbidden
load_dotenv()
groq_api = os.getenv("GROQ_API_KEY")
from .forms import BrandForm
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from decimal import Decimal
from django.core.mail import send_mail
from django.urls import reverse
from django.http import JsonResponse, Http404

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

            text = request.POST.get('text', '').strip()
            stars = request.POST.get('stars', '').strip()

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




@login_required
def ai_help(request):
    answer = ""
    prompt = request.POST.get('prompt', '').strip() if request.method == "POST" else ""

    if prompt:
        past_chats = AIChatHistory.objects.filter(user=request.user).order_by('timestamp')[:10]
        past_chats_list = list(past_chats)


        client = Groq(api_key=groq_api)


        traders_stats = []
        
        all_users = User.objects.annotate(
            cars_count=Count('car', distinct=True),
            reviews_count=Count('car__reviews', distinct=True),
            sales_count=Count('car__order', filter=Q(car__order__status='paid'), distinct=True),
            credits_count=Count('car__credit', filter=Q(car__credit__status='approved'), distinct=True)
        )

        for member in all_users:
            activity = UserActivity.objects.filter(user=member).first()
            live_seconds = activity.total_seconds if activity else 0
            live_minutes = round(live_seconds / 60, 1)

            total_sales = member.sales_count + member.credits_count

            display_name = f"{member.username} (Admin)" if member.is_superuser else member.username

            if member.cars_count > 0 or total_sales > 0 or member.reviews_count > 0 or live_minutes > 0:
                traders_stats.append({
                    'username': display_name,
                    'cars_in_stock': member.cars_count,
                    'total_reviews': member.reviews_count,
                    'live_time_minutes': live_minutes,
                    'successful_sales': total_sales
                })

        admin_user_stats = next((item for item in traders_stats if "Admin" in item['username']), None)
        if admin_user_stats:
            null_cars = Car.objects.filter(owner__isnull=True)  
            admin_user_stats['cars_in_stock'] += null_cars.count()
            
            for n_car in null_cars:
                if hasattr(n_car, 'reviews'):
                    admin_user_stats['total_reviews'] += n_car.reviews.count()
                if hasattr(n_car, 'order_set'):
                    admin_user_stats['successful_sales'] += n_car.order_set.filter(status='paid').count()
                if hasattr(n_car, 'credit_set'):
                    admin_user_stats['successful_sales'] += n_car.credit_set.filter(status='approved').count()

        traders_stats = sorted(
            traders_stats, 
            key=lambda x: (x['successful_sales'], x['total_reviews'], x['live_time_minutes'], x['cars_in_stock']), 
            reverse=True
        )

        traders_ranking_text = ""
        for index, t in enumerate(traders_stats, 1):
            traders_ranking_text += f"{index}. {t['username']} | Успешных сделок: {t['successful_sales']} | Отзывов на авто: {t['total_reviews']} | Время онлайн: {t['live_time_minutes']} мин. | Машин в наличии: {t['cars_in_stock']}\n"

        if not request.user.is_superuser and hasattr(request.user, 'license') and request.user.license.is_active:
            cars = Car.objects.filter(owner=request.user).select_related('model')
        else:
            cars = Car.objects.select_related('model')
            
        cars_for_ai = []
        for car in cars:
            cars_for_ai.append({
                'name': car.title,
                'price': float(car.price),
                'brand': car.model.brand.name if hasattr(car.model, 'brand') else "Unknown",
                'model': car.model.name,
                'owner': car.owner.username if getattr(car, 'owner', None) else "Admin"
            })

        system_prompt = f"""
You are OrderCar AI assistant. 
Help users choose cars and recommend the best traders/sellers based on stats.

Here is the current GLOBAL TRADERS & ADMIN RANKING (Dynamically calculated):
{traders_ranking_text}

Here is the available CARS LIST:
{cars_for_ai}

Rules:
1. Speak friendly and explain simply.
2. Always use emojis elegantly.
3. If a user asks "Who is the best seller/trader?" or "Who has more sales?", look at the GLOBAL RANKING, analyze the stats (including Admin if he is active), and answer dynamically.
4. Recommend cars ONLY from the provided cars list.
"""

        messages_history = [{"role": "system", "content": system_prompt}]
        for chat in past_chats_list:
            messages_history.append({"role": "user", "content": chat.user_message})
            messages_history.append({"role": "assistant", "content": chat.ai_response})

        messages_history.append({"role": "user", "content": prompt})

        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages_history
            )
            answer = response.choices[0].message.content

            AIChatHistory.objects.create(
                user=request.user,
                user_message=prompt,
                ai_response=answer
            )
        except Exception as e:
            answer = "⚠️ Извините, наш ИИ-помощник сейчас обновляет базу данных или перегружен. Пожалуйста, отправьте вопрос еще раз через пару секунд!"

    ai_messages = AIChatHistory.objects.filter(user=request.user).order_by('timestamp')

    return render(
        request,
        'cars/ai_help.html',
        {
            'ai_messages': ai_messages,
            'prompt': prompt,
            'answer': answer
        }
    )

@login_required
def chat_owner(request, car_id=None):
    """Вьюха самого чата внутри машины"""
    car = get_object_or_404(Car, id=car_id)
    
    if request.user == car.owner:
        conversation = Conversation.objects.filter(car=car, owner=request.user).first()
        if not conversation:
            return render(request, "chat/chat.html", {
                "car": car, 
                "error": "Покупатели пока не написали вам по этой машине."
            })
    else:
        conversation, created = Conversation.objects.get_or_create(
            car=car,
            buyer=request.user,
            owner=car.owner
        )

    if request.method == "POST":
        text = request.POST.get("message")
        if text:
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                text=text
            )
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return HttpResponse(status=201)
            
        return redirect("chat_owner", car_id=car.id)

    messages = conversation.messages.order_by("id")
    
    return render(request, "chat/chat.html", {
        "car": car,
        "messages": messages,
        "conversation": conversation
    })


@login_required
def admin_chat_view(request, chat_id=None):
    """Вьюха списка всех чатов (Входящие / Панель админа)"""
    if not chat_id:
        if request.user.is_superuser:
            all_chats = Conversation.objects.all().select_related('buyer', 'car')
        else:
            all_chats = Conversation.objects.filter(
                Q(owner=request.user) | Q(buyer=request.user)
            ).select_related('buyer', 'car')
            
        return render(request, "chat/admin_list.html", {"conversations": all_chats})
    
    conversation = get_object_or_404(Conversation, id=chat_id)
    car = conversation.car

    if request.user != conversation.buyer and request.user != conversation.owner and not request.user.is_superuser:
        return HttpResponseForbidden("У вас нет доступа к этому чату.")

    if request.method == "POST":
        text = request.POST.get("message")
        if text:
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                text=text
            )
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return HttpResponse(status=201)
            
        return redirect("admin_chat_view", chat_id=conversation.id)

    messages = conversation.messages.order_by("id")
    return render(request, "chat/chat.html", {
        "car": car,
        "messages": messages,
        "conversation": conversation
    })

@login_required
def add_car(request):
    if not request.user.is_superuser and not (hasattr(request.user, 'license') and request.user.license.is_active):
        return HttpResponseForbidden("У вас нет активной бизнес-лицензии для добавления машин.")

    if request.method == "POST":
        form = CarForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            car = form.save(commit=False)
            
            if hasattr(car, 'owner'):
                car.owner = request.user
            elif hasattr(car, 'user'):
                car.user = request.user
                
            car.save()

            images = request.FILES.getlist('images')
            for img in images:
                CarImage.objects.create(car=car, image=img)

            return redirect('home')
    else:
        form = CarForm(user=request.user)

    return render(request, "cars/add_car.html", {"form": form})


@login_required
def edit_car(request, car_id):
    car = get_object_or_404(Car, id=car_id)

    is_owner = getattr(car, 'owner', None) == request.user or getattr(car, 'user', None) == request.user
    if not request.user.is_superuser and not is_owner:
        return HttpResponseForbidden("Вы не можете редактировать чужую машину!")

    if request.method == "POST":
        form = CarForm(request.POST, request.FILES, instance=car, user=request.user)
        if form.is_valid():
            form.save()
            return redirect("car_detail", car_id=car.id)
    else:
        form = CarForm(instance=car, user=request.user)

    return render(request, "cars/edit_car.html", {"form": form, "car": car})

@login_required
def delete_car(request, car_id):
    car = get_object_or_404(Car, id=car_id)

    is_owner = getattr(car, 'owner', None) == request.user or getattr(car, 'user', None) == request.user
    if not request.user.is_superuser and not is_owner:
        return HttpResponseForbidden("Вы не можете удалить чужую машину!")

    if request.method == "POST":
        car.delete()
        return redirect("home")

    return render(request, "cars/delete.html", {"car": car})


@login_required
def get_messages_json(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    if request.user != conversation.buyer and not request.user.is_superuser:
        return JsonResponse({"error": "Forbidden"}, status=403)
        
    messages = conversation.messages.order_by("id")
    messages_list = []
    
    for m in messages:
        messages_list.append({
            "sender": m.sender.username,
            "is_me": m.sender == request.user,
            "text": m.text,
            "time": m.created_at.strftime("%H:%M") 
        })
        
    return JsonResponse({"messages": messages_list})

class BrandListView(LoginRequiredMixin, generic.ListView):
    model = Brand
    template_name = 'cars/brand_list.html'  
    context_object_name = 'brands'

    def get_queryset(self):
        return Brand.objects.all()


class BrandDetailView(LoginRequiredMixin, generic.DetailView):
    model = Brand
    template_name = 'cars/brand_detail.html'
    context_object_name = 'brand'

    def get_queryset(self):
        return Brand.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['models'] = CarModel.objects.filter(brand=self.object)
        return context


class BrandCreateView(LoginRequiredMixin, generic.CreateView):
    model = Brand
    form_class = BrandForm
    template_name = 'cars/brand_form.html'
    success_url = reverse_lazy('brand_list')  

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        self.object.save()
        return redirect(self.get_success_url())


class BrandUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Brand
    form_class = BrandForm
    template_name = 'cars/brand_form.html' 
    success_url = reverse_lazy('brand_list')

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Brand.objects.all()
        return Brand.objects.filter(owner=self.request.user)


class BrandDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Brand
    template_name = 'cars/brand_confirm_delete.html'
    success_url = reverse_lazy('brand_list')

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Brand.objects.all()
        return Brand.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.is_deleted = True
        self.object.save()
        return redirect(success_url)

class BrandRestoreView(LoginRequiredMixin, generic.View):
    def get(self, request, pk):
        if not request.user.is_superuser:
            return HttpResponseForbidden("Only superusers can restore brands.")
        
        brand = get_object_or_404(Brand.all_objects, id=pk, is_deleted=True)
        brand.is_deleted = False
        brand.save()
        
        return redirect('profile')


@login_required
def checkout_view(request, car_id, payment_type):
    car = get_object_or_404(Car, id=car_id)
    months = int(request.GET.get('months', 12))
    
    interest_rate = Decimal('0.12')
    total_credit_amount = car.price * (Decimal('1') + interest_rate)
    monthly_payment = round(total_credit_amount / months, 2) if payment_type == 'credit' else 0

    if request.method == 'POST':
        user_phone = request.POST.get('phone')
        user_email = request.POST.get('email')
        
        if payment_type == 'buy':
            Order.objects.create(
                user=request.user,
                car=car,
                status='paid'
            )
        else:
            Credit.objects.create(
                user=request.user,
                car=car,
                amount=total_credit_amount,
                months=months,
                status='approved'
            )

        subject = f"Congratulations on your transaction for {car.title}!"
        message = f"""
        Hello {request.user.username}!
        
        Your transaction to {payment_type} the car {car.title} for ${car.price} has been successfully processed.
        Your contact phone number: {user_phone}
        
        Thank you for choosing CarStore!
        """

        try:
            send_mail(
                subject,
                message,
                's95344349@gmail.com', 
                [user_email],
                fail_silently=True,
            )
        except Exception:
            pass 

        return render(request, 'cars/email_sent.html', {'email': user_email, 'success': True})

    return render(request, 'cars/checkout.html', {
        'car': car,
        'payment_type': payment_type,
        'months': months,
        'monthly_payment': monthly_payment,
        'total_credit_amount': total_credit_amount,
    })


def verify_transaction_view(request, type, action, pk):
    if type == 'buy':
        item = get_object_or_404(Order, id=pk)
        if action == 'confirm':
            item.status = 'paid'  
            template = 'cars/success_buy.html'
        else:
            item.status = 'cancelled' 
            template = 'cars/cancel_buy.html'
        item.save()  
        
    elif type == 'credit':
        item = get_object_or_404(Credit, id=pk)
        if action == 'confirm':
            item.status = 'approved' 
            template = 'cars/success_credit.html'
        else:
            item.status = 'rejected' 
            template = 'cars/cancel_credit.html'
        item.save()  

    return render(request, template, {'item': item})


def check_delivery_access(order_id, user):
    order = Order.objects.filter(id=order_id).first()
    is_credit = False
    
    if not order:
        order = Credit.objects.filter(id=order_id).first()
        is_credit = True
        
    if not order:
        raise Http404("Заказ не найден")
        
    if order.user != user and not user.is_superuser:
        raise Http404("У вас нет доступа")
        
    if is_credit:
        if order.status != 'approved':
            return None, False
    else:
        if order.status in ['pending', 'cancelled']:
            return None, False
            
    return order, is_credit


@login_required
def order_tracking_view(request, order_id):
    order, is_credit = check_delivery_access(order_id, request.user)
    
    if not order:
        return render(request, 'cars/no_delivery.html', {
            'error_message': "Курьер и геолокация недоступны, так как заказ не одобрен или находится в обработке!"
        })
        
    return render(request, 'cars/tracking.html', {'order': order, 'is_credit': is_credit})


@login_required
def order_api_view(request, order_id):
    order, is_credit = check_delivery_access(order_id, request.user)
    
    if not order:
        return JsonResponse({'error': 'Доставка недоступна для текущего статуса'}, status=403)
        
    admin_owner = User.objects.filter(username='admin', is_superuser=True).first()
    if not admin_owner:
        return JsonResponse({'error': 'Администратор не найден'}, status=404)
        
    conversation, created = Conversation.objects.get_or_create(
        buyer=order.user,
        car=order.car,
        defaults={'owner': admin_owner}
    )
    
    if request.method == 'POST':
        text = request.POST.get('text')
        if text:
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                text=text
            )
            return JsonResponse({'status': 'ok'})

    messages_queryset = conversation.messages.all().order_by('created_at')
    messages = [
        {
            'sender': msg.sender.username,
            'text': msg.text,
            'time': msg.created_at.strftime('%H:%M')
        } for msg in messages_queryset
    ]
    
    lat = float(order.latitude) if hasattr(order, 'latitude') and order.latitude else 55.7558
    lon = float(order.longitude) if hasattr(order, 'longitude') and order.longitude else 37.6173
    
    return JsonResponse({
        'latitude': lat,
        'longitude': lon,
        'messages': messages
    })