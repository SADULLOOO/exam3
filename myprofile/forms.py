from django import forms
from .models import Profile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'location', 'photo']

class LicenseApplicationForm(forms.ModelForm):
    agree_to_terms = forms.BooleanField(
        required=True,
        label="I agree to pay mini deal $15k-$20k in month, and agter 6-months trafic will started to get a bit more summs!"
    )
    
    class Meta:
        model = Profile
        fields = ['has_experience', 'cv_file']