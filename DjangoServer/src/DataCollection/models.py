from django.db import models

class User(models.Model):
    phone_number = models.CharField(max_length=12, primary_key=True)
    facebook_token = models.TextField()
    facebook_appid = models.TextField()
    twitter_token = models.TextField()
    twitter_id = models.TextField()
    twitter_secret = models.TextField()
    twitter_screen_name = models.TextField()
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
    user = models.ForeignKey(User)
    participants = models.TextField(unique=True)
    last_updated = models.TextField()
    def __unicode__(self): 
        return self.participants

class sms_message(models.Model):
    conversation = models.ForeignKey(sms_conversation)
    source = models.TextField()
    recipient = models.TextField()
    body = models.TextField()
    created_time = models.TextField()
    def __unicode__(self): 
        return self.body
class facebook_conversation(models.Model):
    user = models.ForeignKey(User)
    message_count = models.IntegerField()
    thread_id = models.TextField(primary_key=True)
    updated_time = models.TextField()
    recipients = models.TextField()
    def __unicode__(self): 
        return self.thread_id
        
        
class facebook_messages(models.Model):
    conversation = models.ForeignKey(facebook_conversation)
    author_id = models.TextField()
    body = models.TextField()
    created_time = models.TextField()
    def __unicode__(self): 
        return self.body

class facebook_activity(models.Model):
    user = models.ForeignKey(User)
    post_id = models.TextField()
    updated_time = models.TextField()
    source_id = models.TextField()
    description = models.TextField()
    message = models.TextField()
    actor_id = models.TextField()
    isPrimaryPost = models.TextField()
    def __unicode__(self): 
        return self.post_id + ", " + self.description + ", " + self.message
        
class facebook_comments(models.Model):
    activity = models.ForeignKey(facebook_activity)
    from_id = models.TextField()
    text = models.TextField()
    comment_id = models.TextField()
    def __unicode__(self): 
        return self.text
                    
class twitter_conversation(models.Model):
    cID = models.TextField(primary_key=True)
    users=models.ManyToManyField(User)
    message_count = models.IntegerField()
    startTime = models.TextField()
    endTime = models.TextField()
    startID=models.CharField(max_length=100)
    endID=models.CharField(max_length=100)
    type = models.IntegerField();

class twitter_direct_conversation(models.Model):
    cID=models.CharField(max_length=100,primary_key=True)
    users=models.ManyToManyField(User)
    message_count = models.IntegerField()
    startTime = models.TextField()
    endTime = models.TextField()
    startID=models.CharField(max_length=100)
    endID=models.CharField(max_length=100)
    type = models.IntegerField();

class twitter_message(models.Model):
    mID = models.CharField(max_length=100,primary_key=True)
    conversations=models.ManyToManyField(twitter_direct_conversation)
    fromID = models.TextField()
    toID = models.TextField()
    body = models.TextField()
    created_time = models.TextField()
    inReplyToStatusID = models.TextField()
    
class twitter_status(models.Model):
    mID = models.CharField(max_length=100,primary_key=True)
    fromID = models.TextField()
    toID = models.TextField()
    body = models.TextField()
    created_time = models.TextField()
    inReplyToStatusID = models.TextField()

# Create your models here.
