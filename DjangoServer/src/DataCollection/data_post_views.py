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


from hashlib import md5
from Crypto.Cipher import AES
from Crypto import Random
import os

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
                            fail(request,"error in post android")
                        else:
                            text = encrypt(key,message.get("text"))
                            if not conversation.sms_message_set.filter(created_time=createdTime):
                                conversation.sms_message_set.create(source = hash(str(message.get("sPID"))) , recipient = hash(str(message.get("dPID")))  ,SmSbody = text ,created_time = createdTime)
        upDateSMS(user)
    except:
        return fail(request, "Error in post android")
    return HttpResponse('worked')
    
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
