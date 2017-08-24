from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import CustomerDetails, Accounts, Transactions, Loans


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'User Name'}),
        }


class Details(forms.ModelForm):
    country = forms.CharField(required=True)
    phone = forms.IntegerField(required=True)
    address = forms.Textarea()


    class Meta:
        model = CustomerDetails
        fields = ( 'country', 'phone', 'address')


class CustomerAccount(forms.ModelForm):
    CURRENCY = (
        ('Dollars', 'Dollars'),
        ('Euro', 'Euro'),
        ('Lira', 'Lira'),
    )
    currency = forms.ChoiceField(choices = CURRENCY, widget=forms.Select(),
                              required=True)

    class Meta:
        model = Accounts
        fields = ('currency',)



class SendMoney(forms.ModelForm):

    receiver = forms.TextInput()

    class Meta:
        model = Transactions
        fields = ('receiver', 'the_amount')

class LoanRequest(forms.ModelForm):
    loan_account = forms.CharField(required=True)
    loan_amount = forms.IntegerField(required=True)

    class Meta:
        model = Loans
        fields = ('loan_account', 'loan_amount')