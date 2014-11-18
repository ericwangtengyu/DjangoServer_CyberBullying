from DataCollection.models import User, twitter_direct_conversation, \
    twitter_conversation, twitter_message, sms_conversation, userInfo, \
    twitter_status, facebook_conversation, facebook_messages, facebook_comments, \
    sms_message,SurveyData,UpdatedDate,facebook_activity

from django.test import TestCase  
from simplecrypt import encrypt,decrypt
from dateutil import parser


key = 'This_is%a#made^up*K3y'

class UtilitiesTests(TestCase):
	def test_encrypt_decrypt(self):
		text = "This is the message to encrypt. It should be the same when it is decrypted."
		encryptText = encrypt(key,text)
		decryptText = str(decrypt(key,encryptText))
		self.assertEqual(decryptText, text)
	
class UserPageTests(TestCase):
	def test_signup_page(self):
		resp = self.client.get('/cyber-bullying/login/')
		self.assertEqual(resp.status_code, 200)
		
		resp = self.client.get('/cyber-bullying/instructions/')
		self.assertEqual(resp.status_code, 200)

		resp = self.client.get('/cyber-bullying/resources/')
		self.assertEqual(resp.status_code, 200)

		resp = self.client.get('/cyber-bullying/text/')
		self.assertEqual(resp.status_code, 200)

