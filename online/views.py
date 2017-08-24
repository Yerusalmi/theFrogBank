import json

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render, render_to_response
from django.contrib import auth
# Create your views here.
from django.template.context_processors import csrf
from django.contrib.auth.models import User
from .forms import RegistrationForm, Details, CustomerAccount, SendMoney, LoanRequest
from django.utils import timezone
from .models import CustomerDetails, Accounts, Transactions, Loans
from django import forms
from django_iban.generator import IBANGenerator



def index(request):

    if request.user.is_authenticated():
        return HttpResponseRedirect("/loggedin/")
    form = {}
    return  render(request, 'online/home.html', {"form": form})


def login_in(request):
    c = {}
    c.update(csrf(request))
    return render_to_response("online/login.html", c)


def auth_view(request):
    username = request.POST.get("username", "")
    password = request.POST.get("password", "")
    user = auth.authenticate(username=username, password=password)

    if user is not None:
        auth.login(request, user)
        return HttpResponseRedirect("/loggedin/")
    else:
        return HttpResponseRedirect("/invalid_login/")



@login_required
def loggedin(request):
    data = {}
    global activeibaan
    if request.method == 'POST':
        data["error"] = ""
        selected_currency = request.POST.get('matchvalue')
        data["selected_currency"] = selected_currency
        print ( selected_currency)
        activeuser = request.user.id
        userdetails = User.objects.get(pk=activeuser)
        moredetails = CustomerDetails.objects.get(username_id=activeuser)

        try:
            accountdetails_list = Accounts.objects.get(the_owner_id=activeuser, currency=selected_currency)

        except ObjectDoesNotExist as e:
            data["account_name"] = ""
            data["amount"] = ""
            data["iban"] = ""
            data["error"] = "You do not have such account!"
            data["restrictsend"] = True
            data["restrictdelete"] = True
            return HttpResponse(json.dumps(data))

        data["account_name"] = accountdetails_list.account_name
        data["amount"] = accountdetails_list.amount
        data["iban"] = accountdetails_list.iban
        data["restrictsend"] = False
        data["restrictdelete"] = False
        activeibaan = accountdetails_list.iban # sending money
        data["account_no"] = accountdetails_list.account_no
        print(accountdetails_list.amount)
        return HttpResponse(json.dumps(data))

    else:

        activeuser = request.user.id
        userdetails = User.objects.get(pk=activeuser)
        moredetails = CustomerDetails.objects.get(username_id=activeuser)
        accountdetails_list = Accounts.objects.filter(the_owner_id=activeuser)
        loan_list = Loans.objects.filter(loan_owner_id=activeuser)

        noloans = True
        if (len(loan_list)) > 0:
            noloans = False


        allowed = True
        if (len(accountdetails_list)) == 3:
            allowed = False

        existing_accs = {"Dollars":False,"Euro":False,"Lira":False}

        for account in accountdetails_list:
            print(account.currency)
            if account.currency == "Dollars":
                existing_accs["Dollars"] = True
            elif account.currency == "Euro":
                existing_accs["Euro"] = True
            elif account.currency == "Lira":
                existing_accs["Lira"] = True
        print(existing_accs)



        for account in accountdetails_list:

            activeibaan = account.iban

            print(activeibaan)
            return render_to_response("online/loggedin.html", {"user":userdetails,
                                                                "moredetails":moredetails,
                                                                "accountdetails":account,
                                                                "newaccount": allowed,
                                                                "existing_accs": existing_accs,
                                                                "account.currency": account.currency,
                                                                "noloans": noloans
                                                                })


def invalid_login(request):
    return render_to_response("online/invalid_login.html")


def logout(request):
    auth.logout(request)
    return render_to_response("online/logged_out.html")


def signup(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        formDetails = Details(request.POST)
        accounting = CustomerAccount(request.POST)
        if form.is_valid():
            new = form.save()
            details = CustomerDetails(username=new)
            details.first_name = new.first_name
            details.last_name = new.last_name
            details.e_mail = new.email
            details.country = request.POST.get('country', None)
            details.phone = request.POST.get('phone', None)
            details.address = request.POST.get('address', None)
            details.save()
            acccounts = Accounts(the_owner=new)
            acccounts.account_name = new.first_name
            currency = request.POST.getlist('currency')
            currency = ("".join(currency))
            acccounts.currency = currency
            generator = IBANGenerator()
            valid_iban = generator.generate(country_code='IL')
            acccounts.iban = valid_iban['generated_iban']
            acccounts.account_no = valid_iban['account']

            acccounts.save()
            new = authenticate(request, username=form.cleaned_data['username'],
                                    password=form.cleaned_data['password1'],
                                    )
            login(request, new)
            return HttpResponseRedirect("/loggedin/")
    else:
        form = RegistrationForm()
        formDetails = Details()
        accounting = CustomerAccount()
    return render(request, "online/signup.html", {
        'form': form,
        'form2': formDetails,
        'form3': accounting,
    })


def sendmoney(request):
    if request.method == 'POST':
        activeuser = request.user.id
        accountdetails = Accounts.objects.get(the_owner_id=activeuser,iban=activeibaan)
        userdetails = User.objects.get(id=activeuser)
        send_form = SendMoney(request.POST)
        try:
            receiver = request.POST.get('receiver')
            receiveraccount = Accounts.objects.get(iban=receiver)
            if receiveraccount.the_owner_id is accountdetails.the_owner_id:
                error_message = {"error": "this is you."}
                send_form = SendMoney()
                return render(request, "online/sendmoney.html", {
                    'send_form': send_form,
                    'accountdetails': accountdetails,
                    'error': error_message,
                })

        except ObjectDoesNotExist as e:
            error_message = {"error": "User with IBAN no: '{}' doesnt exist".format(receiver)}
            send_form = SendMoney()
            return render(request, "online/sendmoney.html", {
                'send_form': send_form,
                'accountdetails': accountdetails,
                'error': error_message,
            })
        print (receiveraccount.currency)
        print (accountdetails.currency  )
        if receiveraccount.currency != accountdetails.currency:
            error_message = {"error": "Currency Mismatch"}
            return render(request, "online/sendmoney.html", {
                'send_form': send_form,
                'accountdetails': accountdetails,
                'error': error_message,
            })

        if send_form.is_valid():
            new = send_form.save(commit=False)
            new.account_name_id = activeuser
            new.receiver_name = userdetails.first_name
            new.currency = accountdetails.currency
            new.save()
            amount_to_send = request.POST.get('the_amount', None)
            if int(amount_to_send) <= 0:
                error_message = {"error": "can't send minus amounts"}
                return render(request, "online/sendmoney.html", {
                    'send_form': send_form,
                    'accountdetails': accountdetails,
                    'error': error_message,
                })

            outstanding_blanace = int(accountdetails.amount) - int(amount_to_send)
            if outstanding_blanace <= 0:
                error_message = {"error": "Not enough funds"}
                return render(request, "online/sendmoney.html", {
                    'send_form': send_form,
                    'accountdetails': accountdetails,
                    'error': error_message,
                })
            accountdetails.amount = outstanding_blanace
            receiveraccount.amount += int(amount_to_send)
            receiveraccount.save()
            accountdetails.save()
            return HttpResponseRedirect("/loggedin/")
    else:
        activeuser = request.user.id
        try:
            accountdetails = Accounts.objects.get(the_owner_id=activeuser, iban=activeibaan)

        except NameError:
            error_message = {"error": "Session Time-Out"}
            return loggedin(request)
        send_form = SendMoney()

        return render(request, "online/sendmoney.html", {
            'send_form': send_form,
            'accountdetails': accountdetails,
        })


def create_new_account(request):
    activeuser = request.user.id
    accountdetails = Accounts.objects.filter(the_owner_id=activeuser)
    if request.method == 'POST':
        form = CustomerAccount(request.POST)
        if form.is_valid():
            new = form.save(commit=False)
            new.the_owner_id = activeuser
            new.account_name = request.POST.get('the_amount')
            new.amount = 0

            generator = IBANGenerator()
            valid_iban = generator.generate(country_code='IL')
            new.iban = valid_iban['generated_iban']
            new.account_no = valid_iban['account']

            print (new.account_name)
            new.save()
            return HttpResponseRedirect("/loggedin/")
    else:
        form = CustomerAccount()

        existing_accs = {"Dollars": False, "Euro": False, "Lira": False}

        for account in accountdetails:
            print(account.currency)
            if account.currency == "Dollars":
                existing_accs["Dollars"] = True
            elif account.currency == "Euro":
                existing_accs["Euro"] = True
            elif account.currency == "Lira":
                existing_accs["Lira"] = True
        print(existing_accs)


        return render(request, "online/new_account.html", {
            'form': form,
            'accountdetails': accountdetails,
            'existing_accs': existing_accs,
        })


def removeacc(request):
    if request.method == 'POST':
        iban = request.POST.get('iban')
        delete = Accounts.objects.get(iban=iban).delete()
        return HttpResponse(json.dumps("deleted"))


def activeacc(request):
    if request.method == 'POST':
        print("iban is: " + str(activeibaan))
        return HttpResponse(json.dumps(str(activeibaan)))


def history(request):
    activeuser = request.user.id
    accounts = Transactions.objects.filter(account_name_id=activeuser)
    all_accs = []
    for account in accounts:
        all_accs.append(account)
    print(all_accs)
    return render(request, "online/history.html", {
        'all_accs': all_accs,
    })

def loan(request):
    activeuser = request.user.id
    loans = Loans.objects.filter(loan_owner_id=activeuser)
    if len(loans) > 0: #if the page is requested by url and if loan account exists, redirect the user.
        return HttpResponseRedirect("/loanhis/")
    if request.method == 'POST':
        form = LoanRequest(request.POST)
        if form.is_valid():
            new = form.save(commit=False)
            loanedamount = new.loan_amount
            loanperiod = new.loan_duration
            loaninterest = new.loan_interest
            outstanding_amount = loanedamount * (1 + loaninterest)
            new.outstanding_loan = outstanding_amount
            new.loan_owner_id = activeuser
            new.save()
        return HttpResponseRedirect("/loanhis/")
    else:
        form = LoanRequest()
        return render(request, "online/loan.html", {
            'form': form,
        })

def loanhis(request):
    activeuser = request.user.id
    loans = Loans.objects.filter(loan_owner_id=activeuser)
    all_loans = []
    for loan in loans:
        all_loans.append(loan)
        print(all_loans)
    return render(request, "online/loan.html", {
        'all_loans': all_loans,
    })