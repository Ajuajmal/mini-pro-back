from django.http import HttpResponse
import base64
import hmac
import hashlib
from urllib import parse

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from account.models import Alumni


from django.http import HttpResponseRedirect
from rest_framework.authtoken.models import Token
from django.contrib.auth import login

def alumniBatchGroups(request):
    return redirect('https://community.alumni-cucek.ml/g')




def community_redirect(request,token):
    key = get_object_or_404(Token.objects.all(), key=token)
    user = key.user
    login(request,user)
    return HttpResponseRedirect("https://community.alumni-cucek.ml/login/")

@login_required
def sso(request):
    payload = request.GET.get('sso')
    signature = request.GET.get('sig')

    if payload is None or signature is None:
        return HttpResponseBadRequest('No SSO payload or signature. Please contact support if this problem persists.')

    ## Validate the payload

    try:
        payload = bytes(parse.unquote(payload), encoding='utf-8')
        print(payload)
        decoded = base64.decodestring(payload).decode('utf-8')
        print(decoded)
        assert 'nonce' in decoded
        assert len(payload) > 0
    except AssertionError:
        return HttpResponseBadRequest('Invalid payload. Please contact support if this problem persists.')

    key = bytes(settings.DISCOURSE_SSO_SECRET, encoding='utf-8') # must not be unicode
    h = hmac.new(key, payload, digestmod=hashlib.sha256)
    this_signature = h.hexdigest()
    print(h.hexdigest())
    print(key)

    if not hmac.compare_digest(this_signature, signature):
        return HttpResponseBadRequest('Invalid payload. Please contact support if this problem persists.')

    ## Build the return payload

    qs = parse.parse_qs(decoded)
    print(qs)
    params = {
        'nonce': qs['nonce'][0],
        'email': request.user.email,
        'external_id': request.user.id,
        'username': request.user.username,
        'require_activation': 'false',
    }

    if request.user.is_alumni:
        alumni = Alumni.objects.get(user=request.user)
        groupname = str(alumni.department)+'-'+str(alumni.batch)
        params['add_groups'] = groupname
    if request.user.is_superuser:
        params['admin'] = 'true'
    return_payload = base64.encodestring(bytes(parse.urlencode(params), 'utf-8'))
    h = hmac.new(key, return_payload, digestmod=hashlib.sha256)
    query_string = parse.urlencode({'sso': return_payload, 'sig': h.hexdigest()})

    ## Redirect back to Discourse

    url = '%s/session/sso_login' % settings.DISCOURSE_BASE_URL
    return HttpResponseRedirect('%s?%s' % (url, query_string))
