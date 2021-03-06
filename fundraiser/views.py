from django.shortcuts import render,get_object_or_404,redirect

from .models import FundRaiserEvent
from django.shortcuts import render
from django.contrib.auth import authenticate, login as auth_login
from django.conf import settings
from .models import Transaction,FundRaiserEvent
from .paytm import generate_checksum, verify_checksum
from django.utils import timezone

from django.views.decorators.csrf import csrf_exempt

from . import Checksum
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .utils import VerifyPaytmResponse
import requests
from .forms import AmountForm

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction

from django.http import HttpResponseRedirect
from rest_framework.authtoken.models import Token
from django.contrib.auth import login

from django.core.mail import EmailMessage
from django.conf import settings
from django.utils.encoding import force_bytes, force_text
from django.template.loader import render_to_string

def sendtxnmail(request,resp,user,event):
    template = 'pay/mail/txn_mail.html'
    email_subject = 'Contribution Acknwldgmnt. '
    message = render_to_string(template, {
    'user': user,
    'event': event.event_name,
    'ORDER_ID' : resp['ORDER_ID'],
    'TXNAMOUNT': resp['TXN_AMOUNT'],
    'STATUS': 'INITIATED',
    })
    to_email = user.email
    email = EmailMessage(email_subject, message, to=[to_email],from_email='alumni@cucek.in')
    email.send()

def fundraiser_redirect(request,token):
    key = get_object_or_404(Token.objects.all(), key=token)
    user = key.user
    login(request,user)
    return HttpResponseRedirect("https://www.alumni-cucek.ml/fundraiser/")

def payment(request,eventid,orderid,amount):
    event = get_object_or_404(FundRaiserEvent, id=eventid)
    print(event.event_name)
    bill_amount = amount
    order_id = orderid
    data_dict = {
        'MID': settings.PAYTM_MERCHANT_ID,
        'INDUSTRY_TYPE_ID': settings.PAYTM_INDUSTRY_TYPE_ID,
        'WEBSITE': settings.PAYTM_WEBSITE,
        'CHANNEL_ID': settings.PAYTM_CHANNEL_ID,
        'CALLBACK_URL': settings.PAYTM_CALLBACK_URL,
        #'MOBILE_NO': '7405505665',
        #'EMAIL': 'dhaval.savalia6@gmail.com',
        'CUST_ID': request.user.username,
        'ORDER_ID':order_id,
        'TXN_AMOUNT': bill_amount,
    } # This data should ideally come from database
    data_dict['CHECKSUMHASH'] = Checksum.generate_checksum(data_dict, settings.PAYTM_MERCHANT_KEY)
    txn = Transaction.objects.get(order_id=order_id)
    txn.checksum = data_dict['CHECKSUMHASH']
    txn.save()
    sendtxnmail(request,data_dict,request.user,event)
    context = {
        'payment_url': settings.PAYTM_PAYMENT_GATEWAY_URL,
        'comany_name': settings.PAYTM_COMPANY_NAME,
        'data_dict': data_dict,
    }
    return render(request, 'pay/payment.html', context)
##Testing OTP credentials are as follows: Mobile Number: 7777777777. Password: Paytm12345. OTP: 489871.
def Amount(request,eventid):
    event = get_object_or_404(FundRaiserEvent, id=eventid)
    txns = Transaction.objects.filter(event=event).filter(made_on__lte=timezone.now()).filter(txn_status='success').order_by('-made_on')
    if request.method == 'POST':
        form = AmountForm(request.POST)
        if form.is_valid():
            order_id = Checksum.__id_generator__()
            amount = form['amount'].value()
            Transaction.objects.create(made_by=request.user,event=event,amount=amount,order_id=order_id,txn_status='init')
            return redirect('payment',eventid=eventid,orderid=order_id,amount=amount)
    else:
        form = AmountForm()
    return render(request, 'pay/pay_form.html', {'form':form, 'event':event, 'txns':txns})
@csrf_exempt
def response(request):
    resp = VerifyPaytmResponse(request)
    print(resp['paytm']['STATUS'])
    if resp['verified']:
        txn = Transaction.objects.get(order_id=resp['paytm']['ORDERID'])
        txn.txn_status='success'
        txn.save()
        fund_event =FundRaiserEvent.objects.get(id=txn.event.id)
        fund_event.raised_amount = fund_event.raised_amount + txn.amount
        fund_event.percentage = (fund_event.raised_amount / fund_event.target_amount) * 100
        fund_event.save()
        messages.success(request, 'successfull transaction')
        return redirect('fundraiser')
    else:
        # check what happened; details in resp['paytm']
        messages.warning(request, 'failed transaction')
        return redirect('fundraiser')

@login_required
def home(request):
    events = FundRaiserEvent.objects.all()
    txns = Transaction.objects.filter(made_on__lte=timezone.now()).filter(txn_status='success').order_by('-made_on')
    return render(request, 'dash/fundraisers.html',{'events':events, 'txns':txns})
