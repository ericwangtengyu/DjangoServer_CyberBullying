from DataCollection.models import User, twitter_direct_conversation, \
    twitter_conversation, twitter_message, sms_conversation, userInfo, \
    twitter_status, facebook_conversation, facebook_messages, facebook_comments, \
    sms_message,SurveyData,UpdatedDate,facebook_activity,facebook_likes
from survey.models import Survey,Question,Choice
from django.shortcuts import render,get_object_or_404
from django.core import serializers
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.http.response import StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import simplejson, encoding, timezone
from django.core.mail import EmailMessage
from DjangoServer import settings
from django.core.urlresolvers import reverse
from googlevoice import Voice

import re
import json
import datetime
import requests
from twython import Twython


from simplecrypt import encrypt,decrypt
from dateutil import parser
from threading import Thread

import DataCollection.views


from hashlib import md5
from Crypto.Cipher import AES
from Crypto import Random
import os


#-----------------------------------------------------------------------
#-----------------------------------------------------------------------
#-----------------------------------------------------------------------
#
#            New User Code
#
#-----------------------------------------------------------------------
#-----------------------------------------------------------------------
#-----------------------------------------------------------------------
# Stops a user from having two sets of survey data if they re-register    
def make_or_remake(phone_number):
    try:
        user = User.objects.get(phone_number = phone_number)
        servey = SurveyData.objects.get(user = user)
    except:
        surveydata = SurveyData(user = user)
        surveydata.save()
        startDate = datetime.datetime(2014,12,12)
        newDate = UpdatedDate(user = user, smsDate = startDate,twitterDate = startDate,facebookDate = startDate)
        newDate.save()
    finally:
        return HttpResponse('PASS')
        
        
@csrf_exempt    
def make_user(request):
    data = json.loads(unicode(request.body, errors='replace'))
    try:
        u = User( encrypted_number = encrypt(DataCollection.views.key , str(data.get("phone_number"))) ,phone_number = hash(str(data.get("phone_number"))) , facebook_token = data.get("facebook_token") , facebook_appid = data.get("facebook_appid") , twitter_token = data.get("twitter_token") , twitter_secret = data.get("twitter_secret") , twitter_screen_name = data.get("twitter_screen_name"), twitter_id = hash(str(data.get("twitter_id"))))   
        u.save()
        user_info=userInfo(user=u,userTimeLineSinceID=1,mentionTimeLineSinceID=1,directMsgSinceID=1,sentDirectMsgSinceID=1)  
        user_info.save()
        make_or_remake(hash(str(data.get("phone_number"))))
    except:
        try:
            u = User(encrypted_number = encrypt(DataCollection.views.key , str(data.get("phone_number"))) ,phone_number = hash(str(data.get("phone_number"))) , twitter_token = data.get("twitter_token") , twitter_secret = data.get("twitter_secret") , twitter_screen_name = data.get("twitter_screen_name"), twitter_id = hash(str(data.get("twitter_id"))))   
            u.save()
            user_info=userInfo(user=u,userTimeLineSinceID=1,mentionTimeLineSinceID=1,directMsgSinceID=1,sentDirectMsgSinceID=1)  
            user_info.save()
            make_or_remake(hash(str(data.get("phone_number"))))
        except:
            try:
                u = User(encrypted_number = encrypt(DataCollection.views.key , str(data.get("phone_number"))) ,phone_number = hash(str(data.get("phone_number"))) , facebook_token = data.get("facebook_token") , facebook_appid = data.get("facebook_appid"))   
                u.save()
                make_or_remake(hash(str(data.get("phone_number"))))
            except:
                try:
                    u = User( encrypted_number = encrypt(DataCollection.views.key , str(data.get("phone_number"))), phone_number = hash(str(data.get("phone_number"))))   
                    u.save()
                    make_or_remake(hash(str(data.get("phone_number"))))
                except:
                    return DataCollection.views.fail(request, "Error in make user")
    
    return HttpResponse('PASS')
    
@csrf_exempt
def emailBackend(request):
    try:
        tempEmail = str(request.POST["email"])
        tempPhone = str(request.POST["phone"])
        tempPhone = re.sub("[^0-9]", "",tempPhone)
        request.session["phone_number"]=tempPhone
        request.session["user_email"]=tempEmail
        return render(request , 'DataCollection/facebookTest.html')
    except:
        return DataCollection.views.fail(request,"email backend failure")

@csrf_exempt
def iphoneLoginBackend(request):
    try:
        temp = str(request.POST["token"]).split("&")
        temp = temp[0].replace("#access_token=","")
        accessTokenRequestString = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id='+ DataCollection.views.facebookAppId + '&client_secret='+ DataCollection.views.facebookSecret + '&fb_exchange_token=' + temp
        facebookResponse= requests.get(accessTokenRequestString)
        facebookResponse = facebookResponse.text
        L = facebookResponse.split("&")
        tempToken = L[0].replace("access_token=","")
        request.session["token"] = tempToken
        return render(request, 'DataCollection/twitterornot.html')
    except:
        return DataCollection.views.fail(request,"iphone login backend failure")

@csrf_exempt
def facebookLoginBackend(request):
    try:
        tempToken = str(request.POST["token"])
        accessTokenRequestString = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id='+ DataCollection.views.facebookAppId + '&client_secret='+ DataCollection.views.facebookSecret + '&fb_exchange_token=' + tempToken 
        facebookResponse= requests.get(accessTokenRequestString)
        facebookResponse = facebookResponse.text
        L = facebookResponse.split("&")
        tempToken = L[0].replace("access_token=","")
        request.session['token']=tempToken
        return render(request, 'DataCollection/twitterornot.html')
    except:
        return DataCollection.views.fail(request,"Facebook login backend failure")

@csrf_exempt
def noTwitter(request):
    try:
        phone_number = request.session["phone_number"]
        token = request.session['token']
        user_email = request.session["user_email"]
        u = User(encrypted_number = encrypt(DataCollection.views.key, phone_number),phone_number = hash(phone_number) , facebook_token = token , facebook_appid = DataCollection.views.facebookAppId , email = user_email)   
        u.save()
        make_or_remake(hash(str(phone_number)))
        return render(request, 'DataCollection/thanks.html')
    except:
        return DataCollection.views.fail(request,"no twitter failure")

@csrf_exempt
def twitterLogin(request):
    twitter = Twython(DataCollection.views.APP_KEY, DataCollection.views.APP_SECRET)
    auth = twitter.get_authentication_tokens(callback_url='http://alacran.cs.uiowa.edu/DataCollection/twittercallback/')
    request.session["OAUTH_TOKEN"] = auth['oauth_token']
    request.session["OAUTH_TOKEN_SECRET"] = auth['oauth_token_secret']
    return HttpResponseRedirect(auth['auth_url'])

@csrf_exempt
def twitterCallBack(request):
    oauth_verifier = request.GET['oauth_verifier']
    twitter = Twython(DataCollection.views.APP_KEY, DataCollection.views.APP_SECRET,request.session['OAUTH_TOKEN'], request.session['OAUTH_TOKEN_SECRET'])
    final_step = twitter.get_authorized_tokens(oauth_verifier)
    twitter_token = final_step['oauth_token']
    twitter_secret = final_step['oauth_token_secret']
    twitter = Twython(DataCollection.views.APP_KEY, DataCollection.views.APP_SECRET,twitter_token, twitter_secret)
    data= twitter.verify_credentials()
    token = request.session["token"]
    user_email = request.session["user_email"]
    phone_number = request.session["phone_number"]
    try:
        u = User( encrypted_number = encrypt( DataCollection.views.key, phone_number) ,email=user_email,phone_number = hash(phone_number) , facebook_token = token , facebook_appid = DataCollection.views.facebookAppId , twitter_token = twitter_token , twitter_secret = twitter_secret , twitter_screen_name = str(data["screen_name"]), twitter_id = hash(str(data.get("twitter_id"))))   
        u.save()
        user_info=userInfo(user=u,userTimeLineSinceID=1,mentionTimeLineSinceID=1,directMsgSinceID=1,sentDirectMsgSinceID=1)  
        user_info.save()
        make_or_remake(hash(str(phone_number)))
        return render(request, 'DataCollection/thanks.html')
    except:
        return DataCollection.views.fail(request,"twitter callback failure")

@csrf_exempt
def emailLogin(request):
    return render(request, 'DataCollection/email.html')

@csrf_exempt
def iphoneBackEnd(request):
    return render(request, 'DataCollection/callback.html')
