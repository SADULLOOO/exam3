from django import forms
from .models import Car, CarImage


class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = [
            'title',
            'model',
            'price',
            'engine',
            'country',
            'description'
        ]


class CarImageForm(forms.ModelForm):
    class Meta:
        model = CarImage
        fields = ['image']