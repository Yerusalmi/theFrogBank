from django.contrib import admin
from .models import CustomerDetails, Accounts, Transactions, Loans
from django.contrib.auth.models import User
# Register your models here.

admin.site.register(Accounts)
admin.site.register(CustomerDetails)
admin.site.register(Transactions)
admin.site.register(Loans)
