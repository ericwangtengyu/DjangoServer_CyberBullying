from django.db import models

class User(models.Model):
    phone_number = models.CharField(max_length=12, primary_key=True)
    has_servey = models.BooleanField(default = False)
    servey = models.TextField(default = "http://www.google.com")
    facebook_token = models.TextField(default = "")
    facebook_appid = models.TextField(default = "")
    twitter_token = models.TextField(default = "")
    twitter_id = models.TextField(default = "")
    twitter_secret = models.TextField(default = "")
    twitter_screen_name = models.TextField(default = "")
    def __unicode__(self): 
        return str(self.phone_number)
    
class userInfo(models.Model):
    user=models.OneToOneField(User, primary_key=True)
    userTimeLineSinceID=models.CharField(max_length=100,default=1)
    mentionTimeLineSinceID=models.CharField(max_length=100,default=1)
    directMsgSinceID=models.CharField(max_length=100,default=1)
    sentDirectMsgSinceID=models.CharField(max_length=100,default=1)
    def __unicode__(self): 
        return str(self.user)
    
class sms_conversation(models.Model):
    user = models.ManyToManyField(User)
    participants = models.TextField(unique=True)
    last_updated = models.CharField(max_length=100)
    def __unicode__(self): 
        return self.participants

class sms_message(models.Model):
    conversation = models.ForeignKey(sms_conversation)
    source = models.CharField(max_length=100)
    recipient = models.CharField(max_length=100)
    body = models.TextField()
    created_time = models.CharField(max_length=100)
    def __unicode__(self): 
        return self.body
class facebook_conversation(models.Model):
    user = models.ManyToManyField(User)
    message_count = models.IntegerField()
    thread_id = models.CharField(max_length=100,primary_key=True)
    updated_time = models.CharField(max_length=50)
    recipients = models.CharField(max_length=100)
    def __unicode__(self): 
        return self.thread_id
        
        
class facebook_messages(models.Model):
    conversation = models.ForeignKey(facebook_conversation)
    author_id = models.CharField(max_length=100)
    body = models.CharField(max_length=100)
    created_time = models.CharField(max_length=50)
    def __unicode__(self): 
        return self.body

class facebook_activity(models.Model):
    user = models.ForeignKey(User)
    post_id = models.CharField(max_length=100)
    updated_time = models.CharField(max_length=50)
    source_id = models.CharField(max_length=100)
    description = models.TextField()
    message = models.TextField()
    actor_id = models.CharField(max_length=100)
    isPrimaryPost = models.CharField(max_length=100)
    def __unicode__(self): 
        return self.post_id + ", " + self.description + ", " + self.message
        
class facebook_comments(models.Model):
    activity = models.ForeignKey(facebook_activity)
    from_id = models.CharField(max_length=100)
    text = models.TextField()
    comment_id = models.CharField(max_length=100)
    def __unicode__(self): 
        return self.text
                    
class twitter_conversation(models.Model):
    cID = models.CharField(max_length=100,primary_key=True)
    users=models.ManyToManyField(User)
    message_count = models.IntegerField()
    startTime = models.CharField(max_length=50)
    endTime = models.CharField(max_length=50)
    startID=models.CharField(max_length=100)
    endID=models.CharField(max_length=100)
    type = models.IntegerField();

class twitter_direct_conversation(models.Model):
    cID=models.CharField(max_length=100,primary_key=True)
    users=models.ManyToManyField(User)
    message_count = models.IntegerField()
    startTime = models.CharField(max_length=50)
    endTime = models.CharField(max_length=50)
    startID=models.CharField(max_length=100)
    endID=models.CharField(max_length=100)
    type = models.IntegerField();

class twitter_message(models.Model):
    mID = models.CharField(max_length=100,primary_key=True)
    conversations=models.ManyToManyField(twitter_direct_conversation)
    fromID = models.CharField(max_length=100)
    toID = models.CharField(max_length=100)
    body = models.CharField(max_length=100)
    created_time = models.CharField(max_length=50)
    inReplyToStatusID = models.CharField(max_length=100)
    
class twitter_status(models.Model):
    mID = models.CharField(max_length=100,primary_key=True)
    fromID = models.CharField(max_length=100)
    toID = models.CharField(max_length=100)
    body = models.CharField(max_length=100)
    created_time = models.CharField(max_length=50)
    inReplyToStatusID = models.CharField(max_length=100)

# Create your models here.
