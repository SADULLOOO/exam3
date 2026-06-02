from django import forms
from .models import CarImage, Car, Brand, CarModel

class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = [
            'model', 'title', 'price', 'year', 'mileage', 
            'engine', 'engine_volume', 'horsepower', 'color', 
            'country', 'transmission', 'fuel_type', 'hybrid', 
            'status', 'description'
        ]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user and 'model' in self.fields:
            if not user.is_superuser:
                from django.db.models import Q
                self.fields['model'].queryset = CarModel.objects.filter(
                    Q(brand__owner=user) | Q(brand__owner__is_superuser=True)
                )
            else:
                self.fields['model'].queryset = CarModel.objects.all()



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