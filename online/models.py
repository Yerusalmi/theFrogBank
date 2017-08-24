from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_iban.fields import IBANField

# Create your models here.


class CustomerDetails(models.Model):
    username = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=20, null=True)
    last_name = models.CharField(max_length=40, null=True)
    e_mail = models.CharField(max_length=300, null=True)
    country = models.CharField(max_length=30, null=True)
    phone = models.CharField(max_length=30, null=True)
    address = models.CharField(max_length=300, null=True)

    def __str__(self):
        return str(self.username)


class Accounts(models.Model):
    CURRENCY = (
        ('Dollars', 'Dollars'),
        ('Euro', 'Euro'),
        ('Lira', 'Lira'),
    )
    the_owner = models.ForeignKey(User, on_delete=models.CASCADE)
    currency = models.CharField(max_length=50, choices=CURRENCY, null=True)
    account_name = models.CharField(primary_key=True ,max_length=100)
    amount = models.IntegerField(default=0)
    iban = IBANField(enforce_database_constraint=True, unique=True)
    account_no = IBANField(enforce_database_constraint=True, unique=True)

    def __str__(self):
        return "Account Owner: {} / {} / {}".format(str(self.the_owner),str(self.iban),str(self.currency))


class Transactions(models.Model):
    account_name = models.ForeignKey('Accounts', on_delete=models.CASCADE)
    receiver = models.CharField(max_length=50, null=True)
    receiver_name = models.CharField(max_length=50, null=True)
    currency = models.CharField(max_length=10, null=True)
    trans_date = models.DateTimeField(auto_now_add=True, blank=True)
    the_amount = models.IntegerField(default=0)

    def __str__(self):
        return "Transaction No: %s" % self.id


class Loans(models.Model):
    loan_owner = models.ForeignKey(User, on_delete=models.CASCADE)
    loan_amount = models.IntegerField(default=0)
    loan_account = models.CharField(max_length=50, null=True)
    loan_duration = models.IntegerField(default=24, null=True)
    loan_interest = models.FloatField(default=0.05, null=True)
    outstanding_loan = models.IntegerField(default=0, null=True)

    def __str__(self):
        return "Loan Owner: %s" % self.loan_owner