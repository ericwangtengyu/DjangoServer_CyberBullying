from DataCollection.models import User, sms_message, facebook_conversation, \
    facebook_messages, twitter_conversation, twitter_message, facebook_comments, \
    facebook_activity, sms_conversation, userInfo, twitter_direct_conversation, \
    twitter_status,SurveyData, UpdatedDate
from django.contrib import admin

class updatedDateInline(admin.TabularInline):
    model = UpdatedDate
    extra = 1
class userAdmin(admin.ModelAdmin):
    inlines = [updatedDateInline]

class facebook_messagesInline(admin.TabularInline):
    model = facebook_messages
    extra = 1
class facebook_conversationAdmin(admin.ModelAdmin):
    inlines = [facebook_messagesInline]

class sms_messageInline(admin.TabularInline):
    model = sms_message
    extra = 1
class sms_conversationAdmin(admin.ModelAdmin):
    inlines = [sms_messageInline]

admin.site.register(User, userAdmin)
admin.site.register(sms_message)
admin.site.register(sms_conversation,sms_conversationAdmin)
admin.site.register(facebook_conversation , facebook_conversationAdmin)
admin.site.register(facebook_messages) 
admin.site.register(twitter_conversation) 
admin.site.register(twitter_direct_conversation)
admin.site.register(twitter_status)
admin.site.register(twitter_message) 
admin.site.register(facebook_comments) 
admin.site.register(facebook_activity)
admin.site.register(userInfo) 
admin.site.register(SurveyData)
admin.site.register(UpdatedDate) 
# Register your models here.
