from django.contrib.auth.forms import UserCreationForm
from django import forms

class CustomUserCreationForm(UserCreationForm):
    phone_number = forms.CharField(
        label='Phone Number',
        max_length=10,
        required=True,
        widget=forms.TextInput(attrs={
            'type': 'tel',
            'pattern': '[0-9]{10}',
            'title': 'Please enter a 10-digit mobile number.'
        })
    )

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('phone_number',)

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')

        if not phone.isdigit():
            raise forms.ValidationError("Phone number must contain only digits.")

        if len(phone) != 10:
            raise forms.ValidationError("Phone number must be 10 digits long.")

        return phone