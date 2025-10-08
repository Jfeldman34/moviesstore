# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms.utils import ErrorList
from .models import UserProfile
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

class CustomErrorList(ErrorList):
    def __str__(self):
        return self.as_divs()

    def as_divs(self):
        if not self:
            return ''
        return '<div class="errorlist">%s</div>' % ''.join(['<div class="error">%s</div>' % e for e in self])

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    country = CountryField(blank_label='Select a country').formfield(
        widget=CountrySelectWidget(attrs={'class': 'form-control'}),
        required=True
    )
    city = forms.CharField(
        max_length=100, 
        required=False, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your city'})
    )
    zip_code = forms.CharField(
        max_length=20, 
        required=False, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your ZIP code'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'country', 'city', 'zip_code')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to all fields
        for field_name in ['username', 'password1', 'password2']:
            self.fields[field_name].widget.attrs['class'] = 'form-control'
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            # Update user profile with location data
            profile = user.profile
            profile.country = self.cleaned_data.get('country')
            profile.city = self.cleaned_data.get('city', '')
            profile.zip_code = self.cleaned_data.get('zip_code', '')
            profile.save()
        
        return user