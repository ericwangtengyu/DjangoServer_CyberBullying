from DataCollection.models import User, twitter_direct_conversation, \
    twitter_conversation, twitter_message, sms_conversation, userInfo, \
    twitter_status, facebook_conversation, facebook_messages, facebook_comments, \
    sms_message,SurveyData,UpdatedDate,facebook_activity

from django.test import TestCase  
from simplecrypt import encrypt,decrypt
from dateutil import parser


key = 'This_is%a#made^up*K3y'

class DataCollectionTests(TestCase):
	def encrypt_decrypt_test(self):
		user = User(phone_number = 123456789)
		conversation=user.sms_conversation_set.create(participants = "[1234567890, 0987654321]" , last_updated = "14047561235")
		createdTime = datetime.datetime.fromtimestamp(float ("14047561235")).strftime('%Y-%m-%d %H:%M:%S')
		text = "This is the message to encrypt. It should be the same when it is decrypted."
		encryptText = encrypt(key,text)
		messsage = conversation.sms_message_set.create(source = "1234567890" , recipient = "0147852369"  ,SmSbody = encrypttext ,created_time = createdTime)
		decryptText = str(decrypt(key,message.SmSbody))
		
