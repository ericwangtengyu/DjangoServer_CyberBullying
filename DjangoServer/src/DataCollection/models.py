from django.db import models
from django.utils import timezone
import datetime
from jsonfield import JSONField

class User(models.Model):
    phone_number = models.CharField(max_length=100,primary_key=True)
    facebook_token = models.TextField(default = "")
    facebook_appid = models.CharField(max_length=100,default = "")
    twitter_token = models.CharField(max_length=100,default = "")
    twitter_id = models.CharField(max_length=200,default = "")
    twitter_secret = models.CharField(max_length=100,default = "")
    twitter_screen_name = models.CharField(max_length=100,default = "")
    email = models.CharField(max_length=100,default="")
    def __unicode__(self): 
        return str(self.phone_number)

class UpdatedDate(models.Model):
	user = models.ForeignKey(User)
	facebookDate = models.DateTimeField(blank=True, null=True)
	twitterDate = models.DateTimeField(blank=True, null=True)
	smsDate = models.DateTimeField(blank=True, null=True)
	
	
class SurveyData(models.Model):
	user = models.ForeignKey(User)
	surveydata = models.TextField(default =  "{}")
	def __unicode__(self):
		return str(self.surveydata)
	   
class userInfo(models.Model):
    user=models.OneToOneField(User, primary_key=True)
    userTimeLineSinceID=models.CharField(max_length=100,default=1)
    mentionTimeLineSinceID=models.CharField(max_length=100,default=1)
    directMsgSinceID=models.CharField(max_length=100,default=1)
    sentDirectMsgSinceID=models.CharField(max_length=100,default=1)
    def __unicode__(self): 
        return str(self.user)

#-----------------------------------------------------------------------
#-----------------------------------------------------------------------
# 
#   SMS models here
#
#-----------------------------------------------------------------------
#-----------------------------------------------------------------------
 
# The model for each SMS conversation
# A conversation is a record of all messages exchanged between people
# using SMS
class sms_conversation(models.Model):
    user = models.ManyToManyField(User)
    participants = models.TextField(unique=True)
    last_updated = models.CharField(max_length=100)
    def __unicode__(self): 
        return self.participants

# The model for each message of an SMS conversation
class sms_message(models.Model):
    conversation = models.ForeignKey(sms_conversation)
    source = models.CharField(max_length=100)
    recipient = models.CharField(max_length=1000)
    #key= models.CharField(primary_key=True , max_length=50)
    SmSbody = models.BinaryField()
    created_time = models.DateTimeField()
    def from_last_day(self):
        return self.created_time >= timezone.now() - datetime.timedelta(hours=19)

#-----------------------------------------------------------------------
#-----------------------------------------------------------------------
# 
#   Facebook models here
#
#-----------------------------------------------------------------------
#-----------------------------------------------------------------------

# The model for each facebook conversation
# A conversation is a record of all messages exchanged between people
# using Facebook's instant messaging
class facebook_conversation(models.Model):
    user = models.ManyToManyField(User)
    message_count = models.IntegerField()
    thread_id = models.CharField(max_length=100,primary_key=True)
    updated_time = models.CharField(max_length=50)
    unread = models.CharField(max_length=50)
    unseen = models.IntegerField()
    recipients = models.CharField(max_length=500)
    
    def __unicode__(self): 
        return self.thread_id
        
# The model for each message of a facebook conversation
# A message in a facebook conversation a message from one of the participants
# in a conversation
class facebook_messages(models.Model):
    mID=models.CharField(max_length=100,primary_key=True)
    conversation = models.ForeignKey(facebook_conversation)
    author_id = models.CharField(max_length=100)
    body = models.BinaryField()
    created_time = models.DateTimeField()
    def from_last_day(self):
        return self.created_time >= timezone.now() - datetime.timedelta(days=1)

# The model for a non conversation activity on Facebook.
# This can be just about anything - wall posts, status updates, posting links
# accepting friend requests, etc.
class facebook_activity(models.Model):
	
	# Main data about the post, non encrypted
    user = models.ForeignKey(User)
    post_id = models.CharField(max_length=100,unique = True)
    updated_time = models.DateTimeField()
    created_time = models.DateTimeField()
    
    # All of the different things text goes into
    caption = models.BinaryField()
    description = models.BinaryField()
    message = models.BinaryField()
    status_type = models.BinaryField()
    story = models.BinaryField()
    story_type = models.BinaryField() # Actually called type in json, but thats a keyword in python
    link = models.BinaryField()
    source = models.BinaryField()
    
    # JSON fields
    story_tags = JSONField()
    with_tags = JSONField()
    message_tags = JSONField()
    privacy = JSONField()
    place = JSONField()
    
    def __unicode__(self): 
        return self.post_id
    def from_last_day(self):
        return self.updated_time >= timezone.now() - datetime.timedelta(days=1)

# The model for Facebook comments
# Facebook comments are the comments that go on Facebook activities.
class facebook_comments(models.Model):
    activity = models.ForeignKey(facebook_activity)
    from_id = models.CharField(max_length=100)
    text = models.BinaryField()
    like_count = models.IntegerField()
    user_likes = models.BooleanField()
    comment_id = models.CharField(max_length=100)
    can_remove = models.BooleanField()
    created_time = models.DateTimeField()
    def from_last_day(self):
        return self.created_time >= timezone.now() - datetime.timedelta(days=1)
# The model for Facebook likes
# Facebook likes are the likes that go on Facebook activities
class facebook_likes(models.Model):
    activity = models.ForeignKey(facebook_activity)
    from_id = models.CharField(max_length=100)
         
#-----------------------------------------------------------------------
#-----------------------------------------------------------------------
# 
#   Twitter models here
#
#-----------------------------------------------------------------------
#-----------------------------------------------------------------------
                    
class twitter_conversation(models.Model):
    cID = models.CharField(max_length=200,primary_key=True)
    users=models.ManyToManyField(User)
    message_count = models.IntegerField()
    startTime = models.CharField(max_length=50)
    endTime = models.CharField(max_length=50)
    startID=models.CharField(max_length=100)
    endID=models.CharField(max_length=100)
    type = models.IntegerField();

class twitter_direct_conversation(models.Model):
    cID=models.CharField(max_length=200,primary_key=True)
    users=models.ManyToManyField(User)
    message_count = models.IntegerField()
    startTime = models.CharField(max_length=50)
    endTime = models.CharField(max_length=50)
    startID=models.CharField(max_length=100)
    endID=models.CharField(max_length=100)
    type = models.IntegerField();

class twitter_message(models.Model):
    mID = models.CharField(max_length=200,primary_key=True)
    conversations=models.ForeignKey(twitter_direct_conversation)
    fromID = models.CharField(max_length=100,)
    toID = models.CharField(max_length=100,)
    body = models.CharField(max_length=500)
    created_time = models.DateTimeField()
    inReplyToStatusID = models.CharField(max_length=100)
    def from_last_day(self):
        return self.created_time >= timezone.now() - datetime.timedelta(days=1)        

class twitter_status(models.Model):
    mID = models.CharField(max_length=100,primary_key=True)
    author = models.ForeignKey(User,null=True,related_name="author")
    mentionor = models.ManyToManyField(User,null=True,related_name="mentionor")
    body = models.CharField(max_length=100)
    created_time = models.DateTimeField()
    inReplyToStatusID = models.CharField(max_length=100,null=True)
    def from_last_day(self):
        return self.created_time >= timezone.now() - datetime.timedelta(days=1)        
# Create your models here.
