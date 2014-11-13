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
from django.core.mail import send_mail, EmailMessage
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


from hashlib import md5
from Crypto.Cipher import AES
from Crypto import Random
import os


ip = 'http://128.255.45.52:7777/'
key = settings.KEY
facebookAppId = settings.FACEAPP_ID
facebookSecret = settings.FACE_SECRET
APP_KEY = settings.TWITTER_CONSUMER_KEY
APP_SECRET = settings.TWITTER_CONSUMER_SECRET
OAUTH_TOKEN = ''
OAUTH_TOKEN_SECRET = ''
tempEmail = ''
tempToken = ''
tempPhone = ''

def sendSMS(number, message):
    user = settings.GVOICE
    password = settings.GVOICE_PASS
    voice = Voice()
    voice.login(user, password)
    voice.send_sms(number, message)

@csrf_exempt
def sendText(request):
    sendSMS('3196369548',"This message is sent from the cyber-bullying server!")
    return HttpResponse("lets see what happens")

@csrf_exempt
def instructions(request):
    return render(request, 'DataCollection/screenshot.html')

@csrf_exempt
def emailBackend(request):
    try:
        global tempEmail
        global tempPhone
        tempEmail = str(request.POST["email"])
        tempPhone = str(request.POST["phone"])
        tempPhone = re.sub("[^0-9]", "",tempPhone)
        return render(request , 'DataCollection/facebookTest.html')
    except:
        import traceback
        exception = traceback.format_exc()
        print exception
        send_mail("DATA ERROR" ,exception,"cyber-bullying@uiowa.edu",["llclaptrapll@gmail.com"])
        return render(request,'DataCollection/fail.html')

@csrf_exempt
def emailLogin(request):
    return render(request, 'DataCollection/email.html')

@csrf_exempt
def iphoneBackEnd(request):
    return render(request, 'DataCollection/callback.html')

@csrf_exempt
def iphoneLoginBackend(request):
    try:
        global tempToken
        temp = str(request.POST["token"]).split("&")
        tempToken = temp[0].replace("#access_token=","")
        print tempToken
        return render(request, 'DataCollection/twitterornot.html')
    except:
        import sys
        exc_type, exc_obj,exc_tb = sys.exc_info()
        print exc_type, exc_obj,exc_tb
        print "iphone backend"
        return render(request,'DataCollection/fail.html')

@csrf_exempt
def facebookLoginBackend(request):
    try:
        global tempToken
        tempToken = str(request.POST["token"])
        accessTokenRequestString = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id='+ facebookAppId + '&client_secret='+ facebookSecret + '&fb_exchange_token=' + tempToken 
        facebookResponse= requests.get(accessTokenRequestString)
        facebookResponse = facebookResponse.text
        L = facebookResponse.split("&")
        tempToken = L[0].replace("access_token=","")
        return render(request, 'DataCollection/twitterornot.html')
    except:
        import sys
        exc_type, exc_obj,exc_tb = sys.exc_info()
        print exc_type, exc_obj,exc_tb
        print "login backend"
        return render(request,'DataCollection/fail.html')

@csrf_exempt
def surveyLogin(request):
    try:
        print str(request.POST)
        tempToken = str(request.POST["token"])
        accessTokenRequestString = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id='+ facebookAppId + '&client_secret='+ facebookSecret + '&fb_exchange_token=' + tempToken 
        facebookResponse= requests.get(accessTokenRequestString)
        facebookResponse = facebookResponse.text
        L = facebookResponse.split("&")
        tempToken = L[0].replace("access_token=","")
        phone_number = hash(re.sub("[^0-9]", "",request.POST["phone_number"]))
        user = User.objects.get(phone_number = phone_number)
        user.facebook_token = tempToken
        user.save()
        date = get_object_or_404(UpdatedDate, user = user )
        survey = buildSurvey(user,phone_number)
        return render(request , 'survey/survey.html',{'survey':survey,'user_id':phone_number, 'date':date})
    except:
        import traceback
        exception = traceback.format_exc()
        print exception
        send_mail("DATA ERROR" ,exception,"cyber-bullying@uiowa.edu",["llclaptrapll@gmail.com"])
        return render(request,'DataCollection/fail.html')

@csrf_exempt
def generateUserDeltas(request):
    try:
        all_users = User.objects.all()
        try:
            saved_file = open("/home/clapp/Documents/DataCollectionDjango/DjangoServer_CyberBullying/DjangoServer/src/jsonDump/phone_num_diffs.txt", "r")
            lines = saved_file.readlines()
        except:
            import traceback
            exception = traceback.format_exc()
            print exception
            print "File not found"
            lines = []
        not_updated = []
        new_users = []
        for user in all_users:
            date_details = UpdatedDate.objects.get(user = user)
            num = user.phone_number
            date = date_details.smsDate
            found = False
            for i, line in enumerate(lines):
                file_num = line.split(",")[0]
                file_date = line.split(",")[1]
                if (file_num == num):
                    found = True
                    lines[i] = file_num + "," + str(date)
                    # if its more than 48 hours old
                    if date == None:
                        pass
                    elif (date < timezone.now() - datetime.timedelta(hours = 48)):
                        not_updated.append(file_num)
            if not found:
                lines.append(num + "," + str(date))
                new_users.append(num)

        saved_file = open("/home/clapp/Documents/DataCollectionDjango/DjangoServer_CyberBullying/DjangoServer/src/jsonDump/phone_num_diffs.txt", "w")
	for line in lines:
            saved_file.write(line + "\n")
        print "New: ", new_users
        print "Not Updated: ", not_updated
        saved_file.close()
    except:
        import traceback
        exception = traceback.format_exc()
        print exception
        send_mail("Error generating the user deltas" ,exception,"cyber-bullying@uiowa.edu",["llclaptrapll@gmail.com"])
        return render(request,'DataCollection/fail.html')
    return render(request, 'DataCollection/thanks.html')
#end def

@csrf_exempt
def sendOutSurvey(request):
    allUser = User.objects.all()
    var = []
    try:
        for x in allUser:
            if(x.email):
                var.append(x.email)
        email = EmailMessage('Cyber-Bullying Survey','Click the link to start you cyber-bullying survey. http://128.255.45.52:7777/DataCollection/startlogin/','cyber-bullying@uiowa.edu', to=var)
        email.send() 
    except:
        import sys
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print exc_type, exc_tb, exc_obj
        print "sendOutSurvey"
    return HttpResponse("emails sent")
        
@csrf_exempt
def startLogin(request):
    return render(request , 'DataCollection/surveyLogin.html')

def mainPage(request):
    return render(request , 'DataCollection/main_page.html')
  
@csrf_exempt
def noTwitter(request):
    global tempToken
    global tempEmail
    global tempPhone
    try:
        u = User( phone_number = hash(tempPhone) , facebook_token = tempToken , facebook_appid = facebookAppId , email = tempEmail)   
        u.save()
        make_or_remake(hash(str(tempPhone)))
        return render(request, 'DataCollection/thanks.html')
    except:
        import traceback
        exception = traceback.format_exc()
        print exception
        send_mail("DATA ERROR" ,exception,"cyber-bullying@uiowa.edu",["llclaptrapll@gmail.com"])
        return render(request,'DataCollection/fail.html')      
         

@csrf_exempt
def app(request):
    return render(request, 'DataCollection/downloadApp.html')

@csrf_exempt
def getHelp(request):
    return HttpResponse("we're here to help")

@csrf_exempt
def twitterLogin(request):
    twitter = Twython(APP_KEY, APP_SECRET)
    auth = twitter.get_authentication_tokens(callback_url='http://128.255.45.52:7777/DataCollection/twittercallback/')
    global OAUTH_TOKEN
    global OAUTH_TOKEN_SECRET
    OAUTH_TOKEN = auth['oauth_token']
    OAUTH_TOKEN_SECRET = auth['oauth_token_secret']
    return HttpResponseRedirect(auth['auth_url'])

@csrf_exempt
def twitterCallBack(request):
    oauth_verifier = request.GET['oauth_verifier']
    twitter = Twython(APP_KEY, APP_SECRET,OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
    final_step = twitter.get_authorized_tokens(oauth_verifier)
    token = final_step['oauth_token']
    secret = final_step['oauth_token_secret']
    twitter = Twython(APP_KEY, APP_SECRET,token, secret)
    data= twitter.verify_credentials()
    global tempToken
    global tempEmail
    global tempPhone
    try:
        u = User( email=tempEmail,phone_number = hash(tempPhone) , facebook_token = tempToken , facebook_appid = facebookAppId , twitter_token = token , twitter_secret = secret , twitter_screen_name = str(data["screen_name"]), twitter_id = hash(str(data.get("twitter_id"))))   
        u.save()
        user_info=userInfo(user=u,userTimeLineSinceID=1,mentionTimeLineSinceID=1,directMsgSinceID=1,sentDirectMsgSinceID=1)  
        user_info.save()
        make_or_remake(hash(str(tempPhone)))
        return render(request, 'DataCollection/thanks.html')
    except:
        import traceback
        exception = traceback.format_exc()
        print exception
        send_mail("DATA ERROR" ,exception,"cyber-bullying@uiowa.edu",["llclaptrapll@gmail.com"])
        return render(request,'DataCollection/fail.html')

@csrf_exempt
def newToken(request):
    try:
        data=json.loads(unicode(request.body, errors='replace'))
        user = User.objects.get(phone_number = data.get("user"))
        user.facebook_token = data.get("facebook_token")
        user.save()
        return HttpResponse("worked")
    except:
        print "new token"
        return HttpResponse("null")

@csrf_exempt
def withdraw(request):
    try:
        data=json.loads(unicode(request.body, errors='replace'))
        text = data.get("user")
        send_mail("WithDraw" ,text,"mclapp08@gmail.com",["llclaptrapll@gmail.com"])
    except:
        HttpResponse("sorry try again later")
    return HttpResponse("Your out")
        

def buildSurvey(user,phone_number):
    thedatetime = datetime.datetime.now().strftime("%Y:%m:%d:%H:%M:%S")
    title = str(phone_number) + "/" + thedatetime
    survey = Survey(title = title)
    survey.save()
    textmessagelist = []
    for conver in user.sms_conversation_set.all():
        for message in conver.sms_message_set.all():
            if message.from_last_day():
                textmessagelist.append("  recipient: " + message.recipient)
                textmessagelist.append("\t message: " + decrypt(key,message.SmSbody))
    facemessagelist = []
    for faceConver in user.facebook_conversation_set.all():
        for faceMessage in faceConver.facebook_messages_set.all():
            if faceMessage.from_last_day():
                facemessagelist.append("  text: " + decrypt(key,faceMessage.body))
    faceactlist = []
    faceComm = []
    for faceact in user.facebook_activity_set.all():
        if faceact.from_last_day():
            if decrypt(key,faceact.message):
                faceactlist.append("  activity:" + decrypt(key,faceact.message))
        for com in faceact.facebook_comments_set.all():
            if decrypt(key,com.text):
                faceComm.append(" comment:" + decrypt(key,com.text))
    twitterStatus = []
    qs = list(twitter_status.objects.filter(author = user))
    for twitterstatus in qs:
        if twitterstatus.from_last_day():
            twitterStatus.append("   twitter status :" + twitterstatus.body + "\n")
    print(textmessagelist)
    if not textmessagelist:
        textmessagelist.append("No text messages sent in last day")
    text = "Text messages form last day: \n" + "\n".join(textmessagelist)
    q1 = survey.question_set.create(text = text,atype=1)
    y1 = q1.choice_set.create(choice_text="Yes")
    n1 = q1.choice_set.create(choice_text="No")
    print(facemessagelist)
    if not facemessagelist:
        facemessagelist.append("No facebook instant massages from last day")
    text2 = "Facebook message form last day: \n" + "\n".join(facemessagelist)+ "\n".join(faceComm)
    q2 = survey.question_set.create(text = text2,atype=1)
    y2 = q2.choice_set.create(choice_text="Yes")
    n2 = q2.choice_set.create(choice_text="No")
    print(faceactlist)
    if not faceactlist:
        faceactlist.append("No facebook activities from last day")
    text4 = "Facebook activities from last day: \n" + "\n".join(faceactlist)
    q4 = survey.question_set.create(text = text4,atype=1)
    y4 = q4.choice_set.create(choice_text="Yes")
    n4 = q4.choice_set.create(choice_text="No")
    if not twitterStatus:
        twitterStatus.append("No new twitter status")
    text3 = "Twitter status form last day: \n" + "\n".join(twitterStatus)
    q3 = survey.question_set.create(text = text3,atype=1)
    y3 = q3.choice_set.create(choice_text="Yes")
    n3 = q3.choice_set.create(choice_text="No")
    return survey



@csrf_exempt
def survey(request):
    try:
        data=json.loads(unicode(request.body, errors='replace'))
        phone_number = hash(str(data.get("user")))
        user = User.objects.get(phone_number = phone_number)
    except:
        import sys
        exc_type, exc_obj,exc_tb = sys.exc_info()
        print exc_type, exc_obj,exc_tb
        print 'Exception: Could not parse JSON'
        HttpResponse(ip+"/DateCollection/")
    else:
        survey = buildSurvey(user,phone_number)
        theIP = ip+'survey/'+str(survey.id)+'/'+str(phone_number)+'/'
        return HttpResponse(theIP)

'''
@csrf_exempt
def survey(request):
    try:
        data=json.loads(request.body)
        phone_number = data.get("user")
        user = User.objects.get(phone_number = phone_number)
        survey = Survey.objects.latest('created_date')
        surveydata_object = SurveyData.objects.get(user = user)
        surveydata_string = surveydata_object.surveydata
        surveydata_dic = eval(str(surveydata_string))
        has_survey = surveydata_dic.get(str(survey.id),'true')
    except:
        import sys
        exc_type, exc_obj,exc_tb = sys.exc_info()
        print exc_type, exc_obj,exc_tb
        return HttpResponse("null")
    else:
        if has_survey is 'true':
            theIP = ip+'survey/'+str(survey.id)+'/'+phone_number+'/'
            return HttpResponse(theIP)
        else:
            return HttpResponse("null")
'''
def upDateSMS(user):
    if UpdatedDate.objects.filter(user = user):
        D = UpdatedDate.objects.get(user = user)
        D.smsDate = timezone.now()
        D.save()                                        
    else:
        newDate = UpdatedDate(user = user, smsDate = timezone.now())
        newDate.save()

def checkDate(user,otherDate):
    if UpdatedDate.objects.filter(user = user):
        D1 = UpdatedDate.objects.get(user = user).smsDate
        D2 = datetime.datetime.fromtimestamp(long(otherDate))
        if D1 < D2 :
            return True
        return False
    else:
        return False

@csrf_exempt    
def postandroid(request):
    try:
        data_to_write_to_file = request.body
        data=json.loads(unicode(request.body, errors='ignore').replace("\u", ""))
        print request.body
        user = User.objects.get(phone_number = hash(str(data.get("user"))))
        
        save_data(data_to_write_to_file, "android", user)
        conversations = data.get("conversation")
        for conver in conversations:
            if checkDate(user, conver.get("endTime")):
                participantsNOHash = eval(str(conver.get("participant")))
                participantsHash = []
                for part in participantsNOHash:
                    participantsHash.append(hash(str(part)))
                try:
                    conversation = sms_conversation.objects.get(participants=str(participantsHash))
                except:
                    user.sms_conversation_set.create(participants = str(participantsHash) , last_updated = conver.get("endTime"))
                    conversation = user.sms_conversation_set.get( participants = str(participantsHash))
                    print "Error inside of post android stuff"
                for message in conver.get("messages"):
                    if checkDate(user,message.get("createTime")):
                        try:
                            createdTime = datetime.datetime.fromtimestamp(float (message.get("createTime"))).strftime('%Y-%m-%d %H:%M:%S')
                        except:
                            import sys
                            exc_type, exc_obj,exc_tb = sys.exc_info()
                            print exc_type, exc_obj,exc_tb
                            print 'Exception: Could not parse JSON FOR SMS'
                        else:
                            text = encrypt(key,message.get("text"))
                            if not conversation.sms_message_set.filter(created_time=createdTime):
                                conversation.sms_message_set.create(source = hash(str(message.get("sPID"))) , recipient = hash(str(message.get("dPID")))  ,SmSbody = text ,created_time = createdTime)
        upDateSMS(user)
    except:
        import traceback
        exception = traceback.format_exc()
        print exception
        send_mail("DATA ERROR" ,exception,"cyber-bullying@uiowa.edu",["llclaptrapll@gmail.com"])
        return render(request,'DataCollection/fail.html')
    return HttpResponse('worked')
    
def dateSetUp(user):
    if UpdatedDate.objects.filter(user = user):
        D = UpdatedDate.objects.get(user = user)
        fDate=D.facebookDate
        fDate=(fDate-datetime.datetime(1970,1,1)).total_seconds()
        fDate=round(fDate)
        return fDate
    else:
        fDate=(timezone.now()-datetime.datetime(1970,1,1)).total_seconds()
        fDate=round(fDate)
        return fDate

def get_all_faceid(request):
    allUser = User.objects.all()
    var = []
    convar = []
    try:
        for x in allUser:
            for con in x.facebook_conversation_set.all():
                convar.append({"thread_id" : con.thread_id , "updated_time": con.updated_time})
            var.append({"phone":x.phone_number ,"registerDate": str(dateSetUp(x)), "token": x.facebook_token , "info" : convar})
    except:
        import sys
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print exc_type, exc_tb, exc_obj
        print "probably not here, but its faceid just in case"
    dump = { "data" : var }
    return HttpResponse(json.dumps(dump), content_type="application/json")

def TdateSetUp(user):
    if UpdatedDate.objects.filter(user = user):
        D = UpdatedDate.objects.get(user = user)
        tDate=D.twitterDate
        if tDate == None:
            return
        tDate=(tDate-datetime.datetime(1970,1,1)).total_seconds()
        tDate=round(tDate)
        return tDate
    else:
        tDate=(timezone.now()-datetime.datetime(1970,1,1)).total_seconds()
        tDate=round(tDate)
        return tDate

def get_all_twitter(request):
    allUser = User.objects.all()
    var = []
    for x in allUser:
        if userInfo.objects.filter(user=x):
            uf=userInfo.objects.get(user=x)
            var.append({"registerDate": str(TdateSetUp(x)),"twitter_token": x.twitter_token ,"twitter_id": x.twitter_id , "twitter_secret": x.twitter_secret,"userTimeLineSinceID": uf.userTimeLineSinceID ,"mentionTimeLineSinceID": uf.mentionTimeLineSinceID , "directMsgSinceID": uf.directMsgSinceID,"sentDirectMsgSinceID":uf.sentDirectMsgSinceID})
        else:
            empty="1"
            var.append({"registerDate": str(TdateSetUp(x)),"twitter_token": x.twitter_token ,"twitter_id": x.twitter_id , "twitter_secret": x.twitter_secret,"userTimeLineSinceID": empty ,"mentionTimeLineSinceID": empty , "directMsgSinceID": empty,"sentDirectMsgSinceID":empty})
    dump = { "data" : var }
    return HttpResponse(json.dumps(dump), content_type="application/json")

def get_all_user(request):
    allUser = User.objects.all()
    data=serializers.serialize("json", allUser)
    print data
    return HttpResponse(data, content_type="application/json")


# Stops a user from having two sets of survey data if they re-register    
def make_or_remake(phone_number):
    try:
        user = User.objects.get(phone_number = phone_number)
        servey = SurveyData.objects.get(user = user)
    except:
        surveydata = SurveyData(user = user)
        surveydata.save()
        newDate = UpdatedDate(user = user, smsDate = timezone.now(),twitterDate = timezone.now(),facebookDate = timezone.now())
        newDate.save()
    finally:
        return HttpResponse('PASS')
        
        
@csrf_exempt    
def make_user(request):
    data = json.loads(unicode(request.body, errors='replace'))
    try:
        u = User( phone_number = hash(str(data.get("phone_number"))) , facebook_token = data.get("facebook_token") , facebook_appid = data.get("facebook_appid") , twitter_token = data.get("twitter_token") , twitter_secret = data.get("twitter_secret") , twitter_screen_name = data.get("twitter_screen_name"), twitter_id = hash(str(data.get("twitter_id"))))   
        u.save()
        user_info=userInfo(user=u,userTimeLineSinceID=1,mentionTimeLineSinceID=1,directMsgSinceID=1,sentDirectMsgSinceID=1)  
        user_info.save()
        make_or_remake(hash(str(data.get("phone_number"))))
    except:
        try:
            u = User( phone_number = hash(str(data.get("phone_number"))) , twitter_token = data.get("twitter_token") , twitter_secret = data.get("twitter_secret") , twitter_screen_name = data.get("twitter_screen_name"), twitter_id = hash(str(data.get("twitter_id"))))   
            u.save()
            user_info=userInfo(user=u,userTimeLineSinceID=1,mentionTimeLineSinceID=1,directMsgSinceID=1,sentDirectMsgSinceID=1)  
            user_info.save()
            make_or_remake(hash(str(data.get("phone_number"))))
        except:
            try:
                u = User( phone_number = hash(str(data.get("phone_number"))) , facebook_token = data.get("facebook_token") , facebook_appid = data.get("facebook_appid"))   
                u.save()
                make_or_remake(hash(str(data.get("phone_number"))))
            except:
                try:
                    u = User( phone_number = hash(str(data.get("phone_number"))))   
                    u.save()
                    make_or_remake(hash(str(data.get("phone_number"))))
                except:
                    import traceback
                    exception = traceback.format_exc()
                    print exception
                    send_mail("DATA ERROR" ,exception,"cyber-bullying@uiowa.edu",["llclaptrapll@gmail.com"])
                    return render(request,'DataCollection/fail.html')
    
    return HttpResponse('PASS')

def upDateFacebook(user):
    if UpdatedDate.objects.filter(user = user):
        D = UpdatedDate.objects.get(user = user)
        D.facebookDate = timezone.now()
        D.save()                                        
    else:
        newDate = UpdatedDate(user = user, facebookDate = timezone.now())
        newDate.save()

def save_data(data_to_write_to_file, type_name, user):
    filename = str(str(timezone.now()) + "_" + str(type_name) + "_" + str(user.phone_number) + ".jsondump")
    
    folder_path = "/home/clapp/Documents/DataCollectionDjango/DjangoServer_CyberBullying/DjangoServer/src/jsonDump/"
    path = os.path.dirname(folder_path)
    if not os.path.exists(path):
        os.makedirs(path)
    f = open(folder_path + filename,'w')
    f.write(data_to_write_to_file)
    f.close()
    
    thread = Thread(target = encrypt_json_file, args = (folder_path, filename,))
    thread.start()
    
#    with open(in_filename, 'rb') as in_file, open(out_filename, 'wb') as out_file:
#        file_decrypt(in_file, out_file, password)
#end def

def encrypt_json_file(folder_path, filename):
    with open(folder_path + filename, 'rb') as in_file, open(folder_path + filename + ".encrypted", 'wb') as out_file:
        file_encrypt(in_file, out_file, key)
    os.remove(folder_path + filename)

def derive_key_and_iv(password, salt, key_length, iv_length):
    d = d_i = ''
    while len(d) < key_length + iv_length:
        d_i = md5(d_i + password + salt).digest()
        d += d_i
    return d[:key_length], d[key_length:key_length+iv_length]

def file_encrypt(in_file, out_file, password, key_length=32):
    bs = AES.block_size
    salt = Random.new().read(bs - len('Salted__'))
    key, iv = derive_key_and_iv(password, salt, key_length, bs)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    out_file.write('Salted__' + salt)
    finished = False
    while not finished:
        chunk = in_file.read(1024 * bs)
        if len(chunk) == 0 or len(chunk) % bs != 0:
            padding_length = (bs - len(chunk) % bs) or bs
            chunk += padding_length * chr(padding_length)
            finished = True
        out_file.write(cipher.encrypt(chunk))

def file_decrypt(in_file, out_file, password, key_length=32):
    bs = AES.block_size
    salt = in_file.read(bs)[len('Salted__'):]
    key, iv = derive_key_and_iv(password, salt, key_length, bs)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    next_chunk = ''
    finished = False
    while not finished:
        chunk, next_chunk = next_chunk, cipher.decrypt(in_file.read(1024 * bs))
        if len(next_chunk) == 0:
            padding_length = ord(chunk[-1])
            chunk = chunk[:-padding_length]
            finished = True
        out_file.write(chunk)

@csrf_exempt     
def facebook_post(request):
    try:
        #SAVE DATA BEFORE DOING THIS (just in case)
        # please
        data_to_write_to_file = request.body
        data = unicode(request.body, errors='ignore')
        data = data.replace("\u", "")
        data = json.loads(data)
        user = User.objects.get(pk = data.get("user"))
        upDateFacebook(user)
        conversations = data.get("conversation_data")
        stream_objects = data.get("stream_data")
        
        save_data(data_to_write_to_file, "facebook", user)

        
        # Update the database with the new conversation data
        handle_facebook_conversations(conversations, user, data)
        
        # Update the database with the new activites
        handle_facebook_activities(stream_objects, user, data)
        
            
    except:
        import traceback
        import sys
        print 'print_exc():'
        traceback.print_exc(file=sys.stdout)
    return HttpResponse('done')

def handle_facebook_activities(stream_objects, user, data):
    for activityJSON in stream_objects:
        # All of the various encrypted fields
        caption =         encrypt(key, str(activityJSON.get("caption", "")))
        description =     encrypt(key, str(activityJSON.get("description", "")))
        post_id =         encrypt(key, str(activityJSON.get("id")))
        message =         encrypt(key, str(activityJSON.get("message", "")))
        object_id =     encrypt(key, str(activityJSON.get("object_id", "")))
        status_type =     encrypt(key, str(activityJSON.get("status_type", "")))
        story =         encrypt(key, str(activityJSON.get("story", "")))
        story_type =     encrypt(key, str(activityJSON.get("type", "")))
        link =             encrypt(key, str(activityJSON.get("link", "")))
        source =         encrypt(key, str(activityJSON.get("source", "")))
        
        # Get the times
        updated_time = parser.parse(activityJSON.get("updated_time")).strftime('%Y-%m-%d %H:%M:%S')
        created_time = parser.parse(activityJSON.get("created_time")).strftime('%Y-%m-%d %H:%M:%S')
        
        # Check if we have this activity already in the database
        if not facebook_activity.objects.filter(post_id = activityJSON.get("id")):
            # We don't, so make one
            user.facebook_activity_set.create( post_id = activityJSON.get("id"), 
                                               updated_time = updated_time, 
                                               created_time = created_time,
                                               caption = caption,
                                               description = description,
                                               message = message,
                                               status_type = status_type,
                                               story = story,
                                               story_type = story_type,
                                               link = link,
                                               source = source,
                                               story_tags = activityJSON.get("story_tags", {}),
                                               with_tags = activityJSON.get("with_tags", {}),
                                               message_tags = activityJSON.get("message_tags", {}),
                                               privacy = activityJSON.get("privacy", {}),
                                               place = activityJSON.get("place", {})
                                             )
                                             
        try:
            if user.facebook_activity_set.filter(post_id = activityJSON.get("id") ): #Only add comments to something we have in the database\
                activity = user.facebook_activity_set.get( post_id = activityJSON.get("id") )
                if type(activityJSON.get("comments").get("data")) != 'NoneType':
                    if len(activityJSON.get("comments").get("data")) != 0:
                        for commentJSON in activityJSON.get("comments").get("data"):
                            text = encrypt(key, commentJSON.get("message"))
                            like_count = commentJSON.get("like_count")
                            from_id = hash(str(commentJSON.get("from").get("id")))
                            user_likes = str(commentJSON.get("user_likes")).upper() == "TRUE"
                            comment_id = commentJSON.get("id")
                            can_remove = str(commentJSON.get("can_remove")).upper() == "TRUE"
                            created_time = parser.parse(commentJSON.get("created_time")).strftime('%Y-%m-%d %H:%M:%S')
                            if not activity.facebook_comments_set.filter(comment_id = comment_id):
                                activity.facebook_comments_set.create( text = text,
                                                                       like_count = like_count,
                                                                       from_id = from_id,
                                                                       user_likes = user_likes,
                                                                       comment_id = comment_id,
                                                                       can_remove = can_remove,
                                                                       created_time = created_time
                                                                     )
                        #end for
                    #end if
                #end if
                if (type(activityJSON.get("likes").get("data"))) != 'NoneType':
                    if len(activityJSON.get("likes").get('data')) != 0:
                        for likeJSON in activityJSON.get("likes").get("data"):
                            if not activity.facebook_likes_set.filter(from_id=likeJSON.get("id")):
                                activity.facebook_likes_set.create(from_id = likeJSON.get("id"))
                        #end for
                    #end if
                #end if
            #endif
        except:
            print "shit, we're here"
            import sys
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print exc_type, exc_tb, exc_obj
    #end for
#end def handle_facebook_activities

def handle_facebook_conversations(conversations, user, data):
    # Loop through the JSON array of all the loaded conversations
    # conversationJSON is the JSONObject representing one conversation
    for conversationJSON in conversations:
        # Check and see if we already have the conversation in the database
        if facebook_conversation.objects.filter(thread_id=conversationJSON.get("id")):
            # We have it
            conversation = facebook_conversation.objects.get(pk=conversationJSON.get("id"))
            conversation.updated_time = parser.parse(conversationJSON.get("updated_time")).strftime("%s")
            
            # If you haven't been added into the database conversation, add your user to it
            if not conversation.user.filter(pk=data.get("user")):
                conversation.user.add(user)
        else:
            # We need to make a new conversation
            
            # First we need the recipients, hash them, and add them to a list
            to_list = conversationJSON.get("to").get("data")
            hashed_recipient_list = []
            for recipientJSON in to_list:
                hashed_recipient_list.append(hash(str(recipientJSON.get("id"))))
            
            # Now we need the message count
            message_count = len(conversationJSON.get("comments").get("data"))
            # String to time in seconds
            updatedTime = parser.parse(conversationJSON.get("updated_time")).strftime("%s")
            
            # Now we create it
            conversation = facebook_conversation( message_count = message_count,
                                                  thread_id = conversationJSON.get("id"),
                                                  updated_time = updatedTime,
                                                  recipients = str(hashed_recipient_list),
                                                  unread = conversationJSON.get("unread"),
                                                  unseen = conversationJSON.get("unseen")
                                                )
            conversation.save()
            conversation.user.add(user)
            conversation = user.facebook_conversation_set.get( pk = conversationJSON.get("id"))
        #end if
        
        # Now we need to update the conversation object with the messages
        # (I know it says comments, thats just how facebook rolls. Its actually messages)
        for messageJSON in conversationJSON.get("comments").get("data"):
            # If the message isn't in the conversation, add it
            if not facebook_messages.objects.filter(pk=messageJSON.get("id")):
                
                createdTime = parser.parse(messageJSON.get("created_time")).strftime('%Y-%m-%d %H:%M:%S')
                
                # Encrypt the text of what the user is saying
                text = encrypt(key,messageJSON.get("message"))
                
                # Hash the user id the message is from
                hashed_from = hash(str(messageJSON.get("from").get("id")))
                
                # Create and add the message
                conversation.facebook_messages_set.create(mID=messageJSON.get("id"),
                                                          author_id = hashed_from, 
                                                          body = text, 
                                                          created_time = createdTime
                                                          )
            #end if
        #end for
        conversation.save()
    #end for
#end def handle_facebook_conversations


def upDateTwitter(user):
    if UpdatedDate.objects.filter(user = user):
        D = UpdatedDate.objects.get(user = user)
        D.twitterDate = timezone.now()
        D.save()                                        
    else:
        newDate = UpdatedDate(user = user, twitterDate = timezone.now())
        newDate.save()
#tengyu is no longer use twitter_post however he suggest I leave the code in 
@csrf_exempt     
def twitter_post(request):
    try:
        #Dump this data before replacing all mean characters
        result = json.loads(unicode(request.body, errors='replace'))
        print "step0"
        userTwitterID=result.get("user")
        conversationData=result.get("conversationData")
        p=User.objects.get(twitter_id=userTwitterID)
        #userInfo.objects.filter(user=p).update(userTimeLineSinceID=result.get("userTimeLineSinceID"),mentionTimeLineSinceID=result.get("mentionTimeLineSinceID"),directMsgSinceID=result.get("directMsgSinceID"),sentDirectMsgSinceID=result.get("sentDirectMsgSinceID"))
        print "step1"
        print conversationData
        for conversation in conversationData: 
            print "step2"
            print conversation
            if twitter_conversation.objects.filter(endID=conversation.get("EndID")):
                print "Already Exists"
                return 
            else:
                print conversation.get("StartID")
                c=twitter_conversation(cID=conversation.get("CID"),startID=conversation.get("StartID"),endID=conversation.get("EndID"),startTime=conversation.get("StartTime"),endTime=conversation.get("EndTime"),message_count=conversation.get("MessageCount"),type=conversation.get("Type"))
                print "step3"
            try:
                c.save();
            except:
                import sys
                exc_type, exc_obj, exc_tb = sys.exc_info()
                print exc_type, exc_tb, exc_obj
                print "please no"
            c.users.add(p);
            print "step4"
            messages=conversation.get("messages")
            for message in messages:
                print "step5"
                toIDStr=message.get("To")
                date = parser.parse(message.get("CreateTime")).strftime('%Y-%m-%d %H:%M:%S')
                m=twitter_message(mID=message.get("MID"),fromID=message.get("From"),created_time=message.get("Text"),body=text)
                if toIDStr:
                    m.toID=toIDStr
                str1=message.get("InReplyToStatusID")
                if str1:
                    m.inReplyToStatusID=str1
                print "step6"
                m.save()
                print "step7"
                print c.cID
                m.conversations.add(c)    
                print "step8"   
    except:
        print 'Exception: Could not parse JSON'
    return HttpResponse('done')

@csrf_exempt     
def twitter_post_separate(request):
    try:
        data_to_write_to_file = request.body
        result = json.loads(unicode(request.body, errors='replace'))
        userTwitterID=result.get("user")
        conversationData=result.get("conversationData")
        statusData=result.get("statusData")
        p=User.objects.get(twitter_id=userTwitterID)
        
        save_data(data_to_write_to_file, "twitter", user = p)
        upDateTwitter(p)
        userInfo.objects.filter(user=p).update(userTimeLineSinceID=result.get("userTimeLineSinceID"),mentionTimeLineSinceID=result.get("mentionTimeLineSinceID"),directMsgSinceID=result.get("directMsgSinceID"),sentDirectMsgSinceID=result.get("sentDirectMsgSinceID"))
        for conversation in conversationData: 
            if twitter_direct_conversation.objects.filter(cID=conversation.get("CID")):
                c=twitter_direct_conversation.objects.get(cID=conversation.get("CID"))
            else:
                c=twitter_direct_conversation(cID=conversation.get("CID"),startID=conversation.get("StartID"),endID=conversation.get("EndID"),startTime=conversation.get("StartTime"),endTime=conversation.get("EndTime"),message_count=conversation.get("MessageCount"),type=conversation.get("Type"))
                c.save();
            c.users.add(p);
            messages=conversation.get("messages")
            for message in messages:
                if not twitter_message.objects.filter(mID=message.get("MID")):
                    date = parser.parse(message.get("CreateTime")).strftime('%Y-%m-%d %H:%M:%S')
                    c.twitter_message_set.create(mID=message.get("MID"),fromID=hash(str(message.get("From"))),toID=hash(str(message.get("To"))),created_time=date,body=message.get("Text")) 
        for status in statusData:
            if twitter_status.objects.filter(mID=status.get("MID")):
                continue
            date = parser.parse(status.get("CreateTime")).strftime('%Y-%m-%d %H:%M:%S')
            s=twitter_status(mID=status.get("MID"),created_time=date,body=status.get("Text"))
            s.save()
            if User.objects.filter(twitter_id=hash(str(status.get("From")))):
                s.author=User.objects.get(twitter_id=hash(str(status.get("From"))))
                s.save()
            toIDStr=status.get("To")   
            if toIDStr:
                strList=toIDStr.split(",")
                for userID in strList:
                    if User.objects.filter(twitter_id=hash(str(userID))):
                        u=User.objects.get(twitter_id=hash(str(userID)))
                        s.mentionor.add(u)
            inReplyToIDStr=status.get("InReplyToStatusID")
            if inReplyToIDStr:
                s.inReplyToStatusID=inReplyToIDStr
                s.save()
    except:
        import sys
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print exc_type, exc_tb, exc_obj
        print "Twitter post error"
    return HttpResponse('done')

@csrf_exempt     
def unify_collect(request):
    '''
    result = json.loads(request.body)
    phoneNum = hash(str(result.get("phoneNum")))
    startDate = result.get("startDate")
    endDate = result.get("endDate")
    startDateTime = datetime.datetime.fromtimestamp(float(startDate)/1000.0).strftime('%Y-%m-%d %H:%M:%S')
    print startDateTime
    endDateTime = datetime.datetime.fromtimestamp(float(endDate)/1000.0).strftime('%Y-%m-%d %H:%M:%S')
    print endDateTime
    user = User.objects.get(pk=phoneNum)
    try:
        print "Step1"
        tDirectConvers = user.twitter_direct_conversation_set.filter(endTime__gte=startDate, endTime__lte=endDate)
        tMessage = twitter_message.objects.filter(conversations__in=tDirectConvers)
        print "Step2"
        tStatus = twitter_status.objects.filter(created_time__gte=startDateTime, created_time__lte=endDateTime).filter(Q(mentionor__phone_number__exact=user.phone_number)|Q(author=user))
        print "Step2.1"
        fDirectConvers = user.facebook_conversation_set.filter(updated_time__gte=startDate, updated_time__lte=endDate)
        fMessages = facebook_messages.objects.filter(conversation__in=fDirectConvers)
        fMList=[]
        for fM in fMessages:
            fMList.append(str(decrypt(key,fM.body)))
        
        fActivity = user.facebook_activity_set.filter(updated_time__gte=startDateTime, updated_time__lte=endDateTime)
        fAList=[]
        for fA in fActivity:
            fAList.append(str(decrypt(key,fA.message)))
            
        fComments = facebook_comments.objects.filter(activity__in=fActivity)
        fCList=[]
        for fC in fComments:
            fCStr=str(decrypt(key,fC.text))
            fCList.append(fCStr)
        print "Step3"
    
        SMSConversation = user.sms_conversation_set.filter(last_updated__gte=startDate, last_updated__lte=endDate)
        print SMSConversation
        SMSMessage= sms_message.objects.filter(conversation__in=SMSConversation)
        smList=[]
        for SM in SMSMessage:
            smsStr=str(decrypt(key,SM.SmSbody))
            smList.append(smsStr)
        print "Step4"
        t1= simplejson.loads(serializers.serialize("json", tDirectConvers))
        t2= simplejson.loads(serializers.serialize("json", tMessage))
        t3= simplejson.loads(serializers.serialize("json", tStatus))
        f1= simplejson.loads(serializers.serialize("json", fDirectConvers))
        f2= simplejson.loads(serializers.serialize("json", fMessages))
        f3= simplejson.loads(serializers.serialize("json", fActivity))
        f4= simplejson.loads(serializers.serialize("json", fComments))
        s1= simplejson.loads(serializers.serialize("json", SMSConversation))
        s2= simplejson.loads(serializers.serialize("json", SMSMessage))
        for i in range(len(s2)):
            s2[i]['fields']['SmSbody']=smList[i]
        for i in range(len(f4)):
            f4[i]['fields']['text']=fCList[i]
        for i in range(len(f2)):
            f2[i]['fields']['body']=fMList[i]
        for i in range(len(f3)):
            f3[i]['fields']['body']=fAList[i]
        print "Step5"
        jsonData=simplejson.dumps( {'twitterDirectConversation':t1, 'twitterMessage':t2,'twitterStatus':t3,'facebookDirectConversation':f1,'facebookMessage':f2,'facebookActivity':f3,'facebookComments':f4,'SMSConversation':s1,'SMSMessage':s2} )
    except:
        import sys
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print exc_type, exc_tb, exc_obj
    return StreamingHttpResponse(jsonData, content_type="application/json")
'''
    return HttpResponse('done')
    
    
def resources(request):
    return render(request , 'DataCollection/resources.html')

def faculty(request):
    return render(request, 'DataCollection/faculty.html')

