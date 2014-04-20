from DataCollection.models import User, twitter_direct_conversation, \
    twitter_conversation, twitter_message, sms_conversation, userInfo, \
    twitter_status, facebook_messages, facebook_conversation
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
@csrf_exempt
def index(request):
    return HttpResponse("Hello, world. You're at the poll index.")

@csrf_exempt    
def postandroid(request):
    print 'Post from Android'
    try:
        data=json.loads(request.body)
        user = User.objects.get( phone_number = data.get("user"))
        conversations = data.get("conversation")
        for conver in conversations:
            try:
                conversation = user.sms_conversation_set.get( participants = conver.get("participants"))
            except:
                user.sms_conversation_set.create(participants = conver.get("participant") , last_updated = conver.get("endTime"))
                conversation = user.sms_conversation_set.get( participants = conver.get("participant"))
            for message in conver.get("messages"):
                try:
                    conversation.sms_message_set.get(created_time = message.get("createTime"))
                except:
                    conversation.sms_message_set.create(source = message.get("sPID") , recipient = message.get("dPID")  ,body = message.get("text") ,created_time = message.get("createTime"))
    except:
        import sys
        exc_type, exc_obj,exc_tb = sys.exc_info()
        print exc_type, exc_obj,exc_tb
        print 'Exception: Could not parse JSON'
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
        uf=userInfo.objects.get(user=x)
        var.append({"twitter_token": x.twitter_token ,"twitter_id": x.twitter_id , "twitter_secret": x.twitter_secret,"userTimeLineSinceID": uf.userTimeLineSinceID ,"mentionTimeLineSinceID": uf.mentionTimeLineSinceID , "directMsgSinceID": uf.directMsgSinceID,"sentDirectMsgSinceID":uf.sentDirectMsgSinceID})
        #var.append({"twitter_token": x.twitter_token ,"twitter_id": x.twitter_id , "twitter_secret": x.twitter_secret})
    dump = { "data" : var }
    return HttpResponse(json.dumps(dump), content_type="application/json")



@csrf_exempt    
def make_user(request):
    print 'got here'
    try:
        data = json.loads(request.body)
        print data
        u = User( phone_number = data.get("phone_number") , facebook_token = data.get("facebook_token") , facebook_appid = data.get("facebook_appid") , twitter_token = data.get("twitter_token") , twitter_secret = data.get("twitter_secret") , twitter_screen_name = data.get("twitter_screen_name"), twitter_id = data.get("twitter_id"))   
        u.save();
        user_info=userInfo(user=u,userTimeLineSinceID=1,mentionTimeLineSinceID=1,directMsgSinceID=1,sentDirectMsgSinceID=1)  
        user_info.save()
    except:
        print 'Exception: Could not parse JSON'
    return HttpResponse('worked')



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
                #conversation = user.facebook_conversation_set.get( pk = conversationData.get("thread_id"))
                conversation=facebook_conversation.objects.get(pk=conversationData.get("thread_id"));
                if not conversation.user.objects.filter(pk=data.get("user")):
                    conversation.user.add(user)
            except:
                conversation=facebook_conversation( message_count= conversationData.get("message_count") , thread_id = conversationData.get("thread_id") ,updated_time = conversationData.get("updated_time") , recipients = conversationData.get("recipients"))
                conversation.save()
                conversation.user.add(user)

                #user.facebook_conversation_set.create( message_count= conversationData.get("message_count") , thread_id = conversationData.get("thread_id") ,updated_time = conversationData.get("updated_time") , recipients = conversationData.get("recipients"))
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
                    conversation.facebook_messages_set.create(m_id=message.get("message_id"),author_id = message.get("author_id") , body = message.get("body"), created_time = message.get("created_time"))
                print "step5"
        
        for streamData in stream_objects:
            print "step_2"
            desc = streamData.get("description")
            if desc == None:
                desc = ""
            mess = streamData.get("message")
            if mess == None:
                mess = ""
            user.facebook_activity_set.create( post_id = streamData.get("post_id"), updated_time = streamData.get("updated_time"), source_id = streamData.get("source_id"), description = desc, message = mess, actor_id = streamData.get("actor_id"), isPrimaryPost = str(len(streamData.get("Comments")) != 0))
            print "step_2.5"
            activity = user.facebook_activity_set.get( post_id = streamData.get("post_id") )
            print "step_3"
            if len(streamData.get("Comments")) != 0:
                for comment in streamData.get("Comments"):
                    print comment
                    activity.facebook_comments_set.create( from_id = comment.get("fromid"), text = comment.get("text"), comment_id = comment.get("id") )
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
                m=twitter_message(mID=message.get("MID"),fromID=message.get("From"),created_time=message.get("CreateTime"),body=message.get("Text"))
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
        #userInfo.objects.filter(user=p).update(userTimeLineSinceID=result.get("userTimeLineSinceID"),mentionTimeLineSinceID=result.get("mentionTimeLineSinceID"),directMsgSinceID=result.get("directMsgSinceID"),sentDirectMsgSinceID=result.get("sentDirectMsgSinceID"))
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
                    c.twitter_message_set.create(mID=message.get("MID"),fromID=message.get("From"),created_time=message.get("CreateTime"),body=message.get("Text"))    
                print "step6" 
        for status in statusData:
            print "step7"
            toIDStr=status.get("To")
            if twitter_status.objects.filter(mID=status.get("MID")):
                continue
            s=twitter_status(mID=status.get("MID"),fromID=status.get("From"),created_time=status.get("CreateTime"),body=status.get("Text"))
            if toIDStr:
                s.toID=toIDStr
            str1=status.get("InReplyToStatusID")
            if str1:
                s.inReplyToStatusID=str1
            print "step8"
            s.save()
            print "step9"   
    except:
        import sys
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print exc_type, exc_tb, exc_obj
    return HttpResponse('done')
