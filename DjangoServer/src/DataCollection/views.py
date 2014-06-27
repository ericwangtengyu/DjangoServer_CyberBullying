from DataCollection.models import User, twitter_direct_conversation, \
    twitter_conversation, twitter_message, sms_conversation, userInfo, \
    twitter_status, facebook_conversation, facebook_messages, facebook_comments, \
    sms_message,SurveyData
from survey.models import Survey,Question,Choice
from django.shortcuts import render
from django.core import serializers
from django.db.models import Q
from django.http import HttpResponse
from django.http.response import StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import simplejson, encoding
from django.core.mail import send_mail

import json
import datetime

from simplecrypt import encrypt,decrypt
from dateutil import parser



ip = 'http://128.255.45.52:7777/'
key = 'This_is%a#made^up*K3y'

@csrf_exempt
def notUser(request):
    return HttpResponse("phone number did not match any users" )
  
@csrf_exempt
def app(request):
    return render(request, 'DataCollection/downloadApp.html')

@csrf_exempt
def getHelp(request):
    return HttpResponse("we're here to help")

@csrf_exempt
def reportBulling(request):
    return HttpResponse("comforting message to get user to report a bully ")
@csrf_exempt
def newToken(request):
    try:
        data=json.loads(request.body)
        user = User.objects.get(phone_number = data.get("user"))
        user.facebook_token = data.get("facebook_token")
        user.save()
        return HttpResponse("worked")
    except:
        return HttpResponse("null")
@csrf_exempt
def withdraw(request):
    try:
        data=json.loads(request.body)
        text = data.get("user")
        send_mail("WithDraw" ,text,"mclapp08@gmail.com",["llclaptrapll@gmail.com"])
    except:
        HttpResponse("sorry try again later")
    return HttpResponse("Your out")
        
@csrf_exempt
def survey(request):
    try:
        data=json.loads(request.body)
        phone_number = data.get("user")
        user = User.objects.get(phone_number = phone_number)
    except:
        import sys
        exc_type, exc_obj,exc_tb = sys.exc_info()
        print exc_type, exc_obj,exc_tb
        print 'Exception: Could not parse JSON'
        HttpResponse(ip+"/DateCollection/")
    else:
        thedatetime = datetime.datetime.now().strftime("%Y:%m:%d:%H:%M:%S")
        title = phone_number + "/" + thedatetime
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
        for faceact in user.facebook_activity_set.all():
            if faceact.from_last_day():
                faceactlist.append("  " + faceact.description)
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
        text2 = "Facebook message form last day: \n" + "\n".join(facemessagelist)
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
        print("step9")
        theIP = ip+'survey/'+str(survey.id)+'/'+phone_number+'/'
        return HttpResponse(theIP)

    
#@csrf_exempt
#def survey(request):
	#try:
		#data=json.loads(request.body)
		#phone_number = data.get("user")
		#user = User.objects.get(phone_number = phone_number)
		#survey = Survey.objects.latest('created_date')
		#surveydata_object = SurveyData.objects.get(user = user)
		#surveydata_string = surveydata_object.surveydata
		#surveydata_dic = eval(str(surveydata_string))
		#has_survey = surveydata_dic.get(str(survey.id),'true')
	#except:
		#import sys
		#exc_type, exc_obj,exc_tb = sys.exc_info()
		#print exc_type, exc_obj,exc_tb
		#return HttpResponse("null")
	#else:
		#if has_survey is 'true':
			#theIP = ip+'survey/'+str(survey.id)+'/'+phone_number+'/'
			#return HttpResponse(theIP)
		#else:
			#return HttpResponse("null")
                                
@csrf_exempt    
def postandroid(request):
	try:
		data=json.loads(request.body)
		print(str(data))
		user = User.objects.get( phone_number = data.get("user"))
		conversations = data.get("conversation")
		for conver in conversations:
			try:
				conversation = sms_conversation.objects.get(participants=conver.get("participant"))
			except:
				user.sms_conversation_set.create(participants = conver.get("participant") , last_updated = conver.get("endTime"))
				conversation = user.sms_conversation_set.get( participants = conver.get("participant"))
			for message in conver.get("messages"):
				print(str(message.get("createTime")))
				print("k1")
				try:
					createdTime = datetime.datetime.fromtimestamp(float (message.get("createTime"))).strftime('%Y-%m-%d %H:%M:%S')
					print("k2")
					print(str(createdTime))
					print("k3")
				except:
					import sys
					exc_type, exc_obj,exc_tb = sys.exc_info()
					print exc_type, exc_obj,exc_tb
					print 'Exception: Could not parse JSON'
				else:
					text = encrypt(key,message.get("text"))
				#try:
					#print("there")
					#conversation.sms_message_set.get(created_time = createdTime)
				#except:'''
					if not conversation.sms_message_set.filter(created_time=createdTime):
						conversation.sms_message_set.create(source = message.get("sPID") , recipient = message.get("dPID")  ,SmSbody = text ,created_time = createdTime)
	except:
		import sys
		exc_type, exc_obj,exc_tb = sys.exc_info()
		print exc_type, exc_obj,exc_tb
		print 'Exception: Could not parse JSON'
		return HttpResponse('Fail')
    #return HttpResponseRedirect(reverse('polls:results', args=(p.id,)))
	return HttpResponse('worked')
    
def get_all_faceid(request):
    allUser = User.objects.all()
    var = []
    convar = []
    try:
        for x in allUser:
            for con in x.facebook_conversation_set.all():
                convar.append({"thread_id" : con.thread_id , "updated_time": con.updated_time})
            var.append({"phone":x.phone_number , "token": x.facebook_token , "info" : convar})
    except:
        import sys
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print exc_type, exc_tb, exc_obj
    dump = { "data" : var }
    return HttpResponse(json.dumps(dump), content_type="application/json")

def get_all_twitter(request):
    allUser = User.objects.all()
    var = []
    for x in allUser:
        if userInfo.objects.filter(user=x):
            uf=userInfo.objects.get(user=x)
            var.append({"twitter_token": x.twitter_token ,"twitter_id": x.twitter_id , "twitter_secret": x.twitter_secret,"userTimeLineSinceID": uf.userTimeLineSinceID ,"mentionTimeLineSinceID": uf.mentionTimeLineSinceID , "directMsgSinceID": uf.directMsgSinceID,"sentDirectMsgSinceID":uf.sentDirectMsgSinceID})
        else:
            empty="1"
            var.append({"twitter_token": x.twitter_token ,"twitter_id": x.twitter_id , "twitter_secret": x.twitter_secret,"userTimeLineSinceID": empty ,"mentionTimeLineSinceID": empty , "directMsgSinceID": empty,"sentDirectMsgSinceID":empty})
    dump = { "data" : var }
    return HttpResponse(json.dumps(dump), content_type="application/json")

def get_all_user(request):
    allUser = User.objects.all()
    data=serializers.serialize("json", allUser)
    print data
    return HttpResponse(data, content_type="application/json")

	
	
# Stops a user from having two sets of survey data if the re-register	
def make_or_remake(phone_number):
    try:
        user = User.objects.get(phone_number = phone_number)
        servey = SurveyData.objects.get(user = user)
    except:
        surveydata = SurveyData(user = user)
        surveydata.save()
    finally:
        return HttpResponse('PASS')
		
		
@csrf_exempt    
def make_user(request):
	data = json.loads(request.body)
	print data
	try:
		u = User( phone_number = data.get("phone_number") , facebook_token = data.get("facebook_token") , facebook_appid = data.get("facebook_appid") , twitter_token = data.get("twitter_token") , twitter_secret = data.get("twitter_secret") , twitter_screen_name = data.get("twitter_screen_name"), twitter_id = data.get("twitter_id"))   
		u.save()
		user_info=userInfo(user=u,userTimeLineSinceID=1,mentionTimeLineSinceID=1,directMsgSinceID=1,sentDirectMsgSinceID=1)  
		user_info.save()
		make_or_remake(data.get("phone_number"))
	except:
		try:
			u = User( phone_number = data.get("phone_number") , twitter_token = data.get("twitter_token") , twitter_secret = data.get("twitter_secret") , twitter_screen_name = data.get("twitter_screen_name"), twitter_id = data.get("twitter_id"))   
			u.save()
			user_info=userInfo(user=u,userTimeLineSinceID=1,mentionTimeLineSinceID=1,directMsgSinceID=1,sentDirectMsgSinceID=1)  
			user_info.save()
			make_or_remake(data.get("phone_number"))
		except:
			try:
				u = User( phone_number = data.get("phone_number") , facebook_token = data.get("facebook_token") , facebook_appid = data.get("facebook_appid"))   
				u.save()
				make_or_remake(data.get("phone_number"))
			except:
				try:
					u = User( phone_number = data.get("phone_number"))   
					u.save()
					make_or_remake(data.get("phone_number"))
				except:
					return HttpResponse('FAIL')
					print 'Exception: Could not parse JSON'
	
	return HttpResponse('PASS')



@csrf_exempt     
def facebook_post(request):
    try:
        data = json.loads(request.body)
        user = User.objects.get(pk = data.get("user"))
        print data.keys()
        conversations = data.get("conversation_data")
        stream_objects = data.get("stream_data")

        for conversationData in conversations:
            print "step2"
            try:
                print " I tryed"
                conversation=facebook_conversation.objects.get(pk=conversationData.get("thread_id"));
                if not conversation.user.objects.filter(pk=data.get("user")):
                    conversation.user.add(user)
            except:
                conversation=facebook_conversation( message_count= conversationData.get("message_count") , thread_id = conversationData.get("thread_id") ,updated_time = conversationData.get("updated_time") , recipients = conversationData.get("recipients"))
                conversation.save()
                conversation.user.add(user)

                print "create"
                conversation = user.facebook_conversation_set.get( pk = conversationData.get("thread_id"))
                print "step3"
            print conversationData.keys()
            for message in conversationData.get("messages"):
                print "step4"
                print message.keys()
                print message
                if not facebook_messages.objects.filter(pk=message.get("message_id")):
                    print "Msg not exist"
                    print conversation.facebook_messages_set.all()
                    createdTime = datetime.datetime.fromtimestamp(message.get("created_time")).strftime('%Y-%m-%d %H:%M:%S')
                    text = encrypt(key,message.get("body"))
                    conversation.facebook_messages_set.create(mID=message.get("message_id"),author_id = message.get("author_id") , body = text, created_time = createdTime)
                print "step5"
        
        for streamData in stream_objects:
            print "step_2"
            desc = streamData.get("description")
            if desc == None:
                desc = ""
            mess = streamData.get("message")
            mess = encrypt(key,mess)
            if mess == None:
                mess = ""
            updated_time = datetime.datetime.fromtimestamp(streamData.get("updated_time")).strftime('%Y-%m-%d %H:%M:%S')
            user.facebook_activity_set.create( post_id = streamData.get("post_id"), updated_time = updated_time, source_id = streamData.get("source_id"), description = desc, message = mess, actor_id = streamData.get("actor_id"), isPrimaryPost = str(len(streamData.get("Comments")) != 0))
            print "step_2.5"
            activity = user.facebook_activity_set.get( post_id = streamData.get("post_id") )
            print "step_3"
            if len(streamData.get("Comments")) != 0:
                for comment in streamData.get("Comments"):
                    print comment
                    text = encrypt(key,comment.get("text"))
                    activity.facebook_comments_set.create( from_id = comment.get("fromid"), text = text, comment_id = comment.get("id") )
                    print "step_4"

    except:
        import sys
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print exc_type, exc_tb, exc_obj
        print 'Exception: Could not parse JSON'
    return HttpResponse('done')
    
@csrf_exempt     
def twitter_post(request):
    try:
        result = json.loads(request.body)
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
        result = json.loads(request.body)
        print "step0"
        userTwitterID=result.get("user")
        conversationData=result.get("conversationData")
        statusData=result.get("statusData")
        p=User.objects.get(twitter_id=userTwitterID)
        userInfo.objects.filter(user=p).update(userTimeLineSinceID=result.get("userTimeLineSinceID"),mentionTimeLineSinceID=result.get("mentionTimeLineSinceID"),directMsgSinceID=result.get("directMsgSinceID"),sentDirectMsgSinceID=result.get("sentDirectMsgSinceID"))
        print "step1"
        for conversation in conversationData: 
            print "step2"
            print conversation
            if twitter_direct_conversation.objects.filter(cID=conversation.get("CID")):
                print "Already Exists"
                c=twitter_direct_conversation.objects.get(cID=conversation.get("CID"))
                
            else:
                print conversation.get("StartID")
                c=twitter_direct_conversation(cID=conversation.get("CID"),startID=conversation.get("StartID"),endID=conversation.get("EndID"),startTime=conversation.get("StartTime"),endTime=conversation.get("EndTime"),message_count=conversation.get("MessageCount"),type=conversation.get("Type"))
                print "step3"
                c.save();
            c.users.add(p);
            print "step4"
            messages=conversation.get("messages")
            for message in messages:
                print "step5"
                if not twitter_message.objects.filter(mID=message.get("MID")):
                    date = parser.parse(message.get("CreateTime")).strftime('%Y-%m-%d %H:%M:%S')
                    c.twitter_message_set.create(mID=message.get("MID"),fromID=message.get("From"),toID=message.get("To"),created_time=date,body=message.get("Text")) 
                print "step6" 
        for status in statusData:
            print "step7"
            if twitter_status.objects.filter(mID=status.get("MID")):
                continue
            date = parser.parse(status.get("CreateTime")).strftime('%Y-%m-%d %H:%M:%S')
            s=twitter_status(mID=status.get("MID"),created_time=date,body=status.get("Text"))
            s.save()
            if User.objects.filter(twitter_id=status.get("From")):
                print("Get here")
                s.author=User.objects.get(twitter_id=status.get("From"))
                print s.author
                s.save()
            toIDStr=status.get("To")   
            if toIDStr:
                print "Mentionors:"
                print toIDStr
                strList=toIDStr.split(",")
                for userID in strList:
                    if User.objects.filter(twitter_id=userID):
                        u=User.objects.get(twitter_id=userID)
                        s.mentionor.add(u)
            inReplyToIDStr=status.get("InReplyToStatusID")
            if inReplyToIDStr:
                print "inReplyToIDStr"
                s.inReplyToStatusID=inReplyToIDStr
                print s.inReplyToStatusID
                s.save()
            print "step8"
            print "step9"   
    except:
        import sys
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print exc_type, exc_tb, exc_obj
    return HttpResponse('done')

@csrf_exempt     
def unify_collect(request):
	result = json.loads(request.body)
	phoneNum = result.get("phoneNum")
	print phoneNum
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
            f3[i]['fields'['body']=fAList[i]
        print "Step5"
        jsonData=simplejson.dumps( {'twitterDirectConversation':t1, 'twitterMessage':t2,'twitterStatus':t3,'facebookDirectConversation':f1,'facebookMessage':f2,'facebookActivity':f3,'facebookComments':f4,'SMSConversation':s1,'SMSMessage':s2} )
    except:
        import sys
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print exc_type, exc_tb, exc_obj
    return StreamingHttpResponse(jsonData, content_type="application/json")
