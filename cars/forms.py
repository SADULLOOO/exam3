from django import forms
from .models import CarImage, Car, Brand

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



class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['name', 'logo']  
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Введите название бренда'
            }),
            'logo': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
        }