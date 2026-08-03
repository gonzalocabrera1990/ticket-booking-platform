from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Address

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'birth',
            'email',
            'dni',
            'img',
            'password1',
            'password2'
        )
class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = (
            'city',
            'street',
            'street_number',
            'floor',
            'apartment',
            'postal_code'
        )