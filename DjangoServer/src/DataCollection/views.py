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


#from DataCollection import new_user_views, date_post_views


import re
import json
import datetime
import requests
from twython import Twython


from simplecrypt import encrypt,decrypt
import simplecrypt
from dateutil import parser
from threading import Thread


from hashlib import md5
from Crypto.Cipher import AES
from Crypto import Random
import os

import new_user_views


ip = 'http://alacran.cs.uiowa.edu/'
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

@csrf_exempt
def getHelp(request):
    print request.GET
    return HttpResponse("temp page and url for quick testing")

def sendSMS(number, message):
    user = settings.GVOICE
    password = settings.GVOICE_PASS
    voice = Voice()
    voice.login(user, password)
    voice.send_sms(number, message)

@csrf_exempt
def sendText(user_list, message):
    for user in user_list:
        sendSMS(decrypt(key, user.encrypted_number) , message)

@csrf_exempt
def text(request):
    return render(request, 'DataCollection/sendText.html')

@csrf_exempt
def textBackend(request):
    try:
        number = User.objects.all()
        if request.POST["phone"]:
            number = [User.objects.get(phone_number = hash(str(re.sub("[^0-9]", "",request.POST["phone"]))))]
        if not request.POST["email"]:
            message = "http://alacran.cs.uiowa.edu/DataCollection/startlogin"
        else:
            message = str(request.POST["email"])
        sendText(number, message)
        return HttpResponse("text message was sent")
    except:
        return fail(request,"Text backend failure")

@csrf_exempt
def surveyPhoneBackend(request):
    try:
        tempPhone = str(request.POST["phone"])
        tempPhone = re.sub("[^0-9]", "",tempPhone)
        return render(request , 'DataCollection/surveyLogin.html',{'phone_number':tempPhone})
    except:
        return fail(request,"email backend failure")
    
@csrf_exempt
def surveyIphoneBackend(request):
    phone_number = request.GET["phone_number"]
    return render(request, 'DataCollection/surveycallback.html',{'phone_number': phone_number})

@csrf_exempt
def surveyLogin(request):
    try:
        phone_number = request.POST["phone_number"]
        hphone_number = hash(phone_number)
        temp = str(request.POST["token"]).split("&")
        if "#" in temp[0]:
            temp = temp[0].replace("#access_token=","")
        else:
            temp = temp[0].replace("access_token=","")
        accessTokenRequestString = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id='+ facebookAppId + '&client_secret='+ facebookSecret + '&fb_exchange_token=' + temp
        facebookResponse= requests.get(accessTokenRequestString)
        facebookResponse = facebookResponse.text
        L = facebookResponse.split("&")
        tempToken = L[0].replace("access_token=","")
        user = User.objects.get(phone_number = hphone_number)
        user.facebook_token = tempToken
        user.save()
        date = get_object_or_404(UpdatedDate, user = user )
        survey = buildSurvey(user,hphone_number)
        return render(request , 'survey/survey.html',{'survey':survey,'user_id':hphone_number, 'date':date})
    except:
        return fail(request,"survey login failure")


@csrf_exempt
def generateUserDeltas(request):
    try:
        all_users = User.objects.all()
        try:
            saved_file = open("/home/clapp/Documents/DataCollectionDjango/DjangoServer_CyberBullying/DjangoServer/src/jsonDump/phone_num_diffs.txt", "r")
            lines = saved_file.readlines()
        except:
            lines = []
        not_updated = []
        new_users = []

        # Go through all the users
        for user in all_users:
            # Get the user's information
            date_details = UpdatedDate.objects.get(user = user)
            num = decrypt(key, user.encrypted_number)
            date = date_details.smsDate
            found = False
            # Go through the file and get the info
            for i, line in enumerate(lines):
                file_num = line.split(",")[0]
                file_date = line.split(",")[1]
                # If the file number equals the user's number
                if (file_num == num):
                    found = True
                    # update the file with the new date from the database
                    lines[i] = file_num + "," + str(date)
                    
                    if date == None or len(str(num)) == 0: # A non cell phone user
                        pass
                    elif (date < timezone.now() - datetime.timedelta(hours = 48)):
                        # If the last time the user was updated was more than 48 hours ago
                        not_updated.append(file_num)
            if not found and date != None and len(num) != 0: # If we didn't find them they're a new user and we need to add them
                lines.append(num + "," + str(date))
                new_users.append(num)

        saved_file = open("/home/clapp/Documents/DataCollectionDjango/DjangoServer_CyberBullying/DjangoServer/src/jsonDump/phone_num_diffs.txt", "w")
	for line in lines:
            saved_file.write(line + "\n")
        email = ""
        email += "New: \n"
        for user in new_users:
                email +=  "\t" + str(user) + "\n"
        email += "Not Updated in the last 48 hours: \n"
        for user in not_updated:
                email +=  "\t" + user + "\n"
        saved_file.close()

#-------------------------------
#   The last updated part
        email += "\n\n\n"
        email += "The last updated times for users\n"
        test_users = ['4103953963257201570','-8559265015842739200', '296267656718926475', '2103970963504202057', '-2850050825785764042','-2453938116241190695','-142739595837066840']
        for dateObj in UpdatedDate.objects.all():
            if dateObj.user_id not in test_users:
                email +=  "User: " + str(dateObj.user_id)
                email +=  "\tFacebook Last Updated: " + str(dateObj.facebookDate)
                if dateObj.twitterDate != parser.parse("2014-12-12"):
                        email += "\tTwitter Last Updated: " + str(dateObj.twitterDate)
                if dateObj.smsDate != parser.parse("2014-12-12"):
                        email += "\tSMS Last Updated: " +str(dateObj.smsDate)

#-------------------------------
        print email
        send_mail("New users and those who haven't updated in 48 hours",email,'cyber-bullying@uiowa.edu', to=["tomwer3@gmail.com"]) #"rebecca-bruening@uiowa.edu","tom-werner@uiowa.edu","dominica-rehbein@uiowa.edu", "octav-chipara@uiowa.edu"])
    except:
        return fail(request,"Error generating user deltas")

    return HttpResponse(email)#render(request, 'DataCollection/thanks.html')
#end def

@csrf_exempt
def sendSurvey(user_list):
    var = []
    try:
        for x in user_list:
            if(x.email):
                var.append(x.email)
        send_mail('Cyber-Bullying Survey','Click the link to start you cyber-bullying survey. http://alacran.cs.uiowa.edu/DataCollection/startlogin/','cyber-bullying@uiowa.edu', to=var)
    except:
        return fail(None,"send survey failure")
    

@csrf_exempt
def sendOutSurvey(request):
    pass
    
  


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
        phone = data.get("user")
        if User.objects.filter(phone_number = hash(phone)):
            user = User.objects.filter(phone_number = hash(phone))
            if UpdatedDate.objects.filter(user = user):
                D = UpdatedDate.objects.get(user = user)
                D.twitterDate = datetime.datetime(2020,1,1)
                D.facebookDate = datetime.datetime(2020,1,1)
                D.save()
    except:
        HttpResponse("sorry try again later")
    return HttpResponse("Your out")
        
@csrf_exempt
def web_withdraw(request):
    return render(request , 'DataCollection/withdraw.html')
    
@csrf_exempt
def web_withdraw_backend(request):
    phone = request.body[6:]
    if User.objects.filter(phone_number = hash(phone)):
        user = User.objects.filter(phone_number = hash(phone))
        if UpdatedDate.objects.filter(user = user):
            D = UpdatedDate.objects.get(user = user)
            D.twitterDate = datetime.datetime(2020,1,1)
            D.facebookDate = datetime.datetime(2020,1,1)
            D.save()
            return render(request, 'DataCollection/withdraw_thanks.html')
    
    return render(request, 'DataCollection/withdraw_fail.html')


def mydecrypt(password, data):
    '''
    Decrypt some data.  Input must be bytes.
    @param password: The secret value used as the basis for a key.
     This should be as long as varied as possible.  Try to avoid common words.
    @param data: The data to be decrypted, typically as bytes.
    @return: The decrypted data, as bytes.  If the original message was a
    string you can re-create that using `result.decode('utf8')`.
    '''
    simplecrypt._assert_not_unicode(data)
    simplecrypt._assert_header_prefix(data)
    print "mydecrypt -- 1"
    version = simplecrypt._assert_header_version(data)
    print "mydecrypt -- 1.1"
    simplecrypt._assert_decrypt_length(data, version)
    print "mydecrypt -- 1.2"
    raw = data[simplecrypt.HEADER_LEN:]
    salt = raw[:simplecrypt.SALT_LEN[version]//8]
    print "mydecrypt -- 2"
    hmac_key, cipher_key = simplecrypt._expand_keys(password, salt)
    hmac = raw[-simplecrypt.HASH.digest_size:]
    hmac2 = simplecrypt._hmac(hmac_key, data[:-simplecrypt.HASH.digest_size])
    simplecrypt._assert_hmac(hmac_key, hmac, hmac2)
    print "mydecrypt -- 3"
    counter = simplecrypt.Counter.new(simplecrypt.HALF_BLOCK, prefix=salt[:simplecrypt.HALF_BLOCK//8])
    cipher = simplecrypt.AES.new(cipher_key, simplecrypt.AES.MODE_CTR, counter=counter)
    r = cipher.decrypt(raw[simplecrypt.SALT_LEN[version]//8:-simplecrypt.HASH.digest_size])
    print "[%s] %d" % (r,len(r))
    return r

def buildSurvey(user,phone_number):
    print "build survey"
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
	    try:
            	md = decrypt(key, faceact.message)
	    except Exception as e:
		print e
	    fmsg = faceact.message
	    #print "new facebook key=[%s] orig=[%s] decrypt=[%s, %d]" % (key, faceact.message, md, len(md))
            if decrypt(key,faceact.message):
                faceactlist.append("  activity:" + decrypt(key,faceact.message))
		#print "added activity", len(faceactlist)
	    else:
		#print "no activity. decrypt failed?"
		pass
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
    text = "Text messages from last day: \n" + "\n".join(textmessagelist)
    q1 = survey.question_set.create(text = text,atype=1)
    y1 = q1.choice_set.create(choice_text="Yes")
    n1 = q1.choice_set.create(choice_text="No")
    print(facemessagelist)
    if not facemessagelist:
        facemessagelist.append("No facebook instant massages from last day")
    text2 = "Facebook message from last day: \n" + "\n".join(facemessagelist)+ "\n".join(faceComm)
    q2 = survey.question_set.create(text = text2,atype=1)
    y2 = q2.choice_set.create(choice_text="Yes")
    n2 = q2.choice_set.create(choice_text="No")
    print("activity list %s %d", str(faceactlist), len(faceactlist))
    if not faceactlist:
        faceactlist.append("No facebook activities from last day")
    text4 = "Facebook activities from last day: \n" + "\n".join(faceactlist)
    q4 = survey.question_set.create(text = text4,atype=1)
    y4 = q4.choice_set.create(choice_text="Yes")
    n4 = q4.choice_set.create(choice_text="No")
    if not twitterStatus:
        twitterStatus.append("No new twitter status")
    text3 = "Twitter status from last day: \n" + "\n".join(twitterStatus)
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
        return fail(request,"survey failure")
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
        return fail(request, "Error in date set up")
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

def upDateFacebook(user):
    if UpdatedDate.objects.filter(user = user):
        D = UpdatedDate.objects.get(user = user)
        D.facebookDate = max(D.facebookDate, timezone.now())
        D.save()
    else:
        newDate = UpdatedDate(user = user, facebookDate = timezone.now())
        newDate.save()

def upDateTwitter(user):
    if UpdatedDate.objects.filter(user = user):
        D = UpdatedDate.objects.get(user = user)
        D.twitterDate = max(D.twitterDate, timezone.now())
        D.save()
    else:
        newDate = UpdatedDate(user = user, twitterDate = timezone.now())
        newDate.save()
        
def updateUserTimes(user, time):
    if UpdatedDate.objects.filter(user = user):
        D = UpdatedDate.objects.get(user = user)
        D.twitterDate = time
        D.save()
    if UpdatedDate.objects.filter(user = user):
        D = UpdatedDate.objects.get(user = user)
        D.facebookDate = time
        D.save()


@csrf_exempt     
def unify_collect(request):
    #Deleted on November 18th. Go find it in git, dammit.
    return HttpResponse('done')


#-----------------------------------------------------------------------
#-----------------------------------------------------------------------
#-----------------------------------------------------------------------
#
#            Render only pages
#
#-----------------------------------------------------------------------
#-----------------------------------------------------------------------
#-----------------------------------------------------------------------
    
def resources(request):
    return render(request , 'DataCollection/resources.html')

def faculty(request):
    return render(request, 'DataCollection/faculty.html')
    
@csrf_exempt
def startLogin(request):
    return render(request , 'DataCollection/startLogin.html')

def mainPage(request):
    return render(request , 'DataCollection/main_page.html')

@csrf_exempt
def instructions(request):
    return render(request, 'DataCollection/screenshot.html')

@csrf_exempt
def sendEmail(request):
    return render(request, 'DataCollection/sendoutsurvey.html')
    
@csrf_exempt
def app(request):
    return render(request, 'DataCollection/downloadApp.html')
    
@csrf_exempt
def privacy(request):
    return render(request, 'DataCollection/confidentiality.html')



#-----------------------------------------------------------------------
#-----------------------------------------------------------------------
#-----------------------------------------------------------------------
#
#            Utilities
#
#-----------------------------------------------------------------------
#-----------------------------------------------------------------------
#-----------------------------------------------------------------------
def fail(request,message):
    import traceback
    exception = traceback.format_exc()
    print exception
    if True:
        return HttpResponse(exception)
    send_mail(message, exception,"cyber-bullying@uiowa.edu",["llclaptrapll@gmail.com"])
    if request:
        return render(request,'DataCollection/fail.html')
            
def send_mail(subject, body, from_email, to):
    email = EmailMessage(subject, body, from_email, to=to)
    email.send()

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
