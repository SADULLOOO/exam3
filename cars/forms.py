from django import forms
from .models import Car
from .models import CarImage
from django import forms

class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = [
            'title',
            'model',
            'price',
            'year',
            'mileage',
            'engine',
            'engine_volume',
            'horsepower',
            'country',
            'color',
            'fuel_type',
            'transmission',
            'status',
            'description'
        ]



class CarImageForm(forms.ModelForm):
    class Meta:
        model = CarImage
        fields = ['image']