
'''
Created on May 23, 2014

@author: maxclapp
'''
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect,HttpResponse
from django.shortcuts import get_object_or_404,render
from django.core import serializers
from .models import Survey, Question,Choice
from DataCollection.models import User, SurveyData
import json

def survey(request , survey_id , user_id):
    survey = get_object_or_404(Survey, pk = survey_id )
    return render(request , 'survey/survey.html',{'survey':survey,
													'user_id':user_id})
    

def answer(request,survey_id,user_id):
	survey = get_object_or_404(Survey, pk = survey_id )
	for question in survey.question_set.all():
		if int(question.atype) == 1:
			try:
				choice_id = request.POST[str(question.id)]
				answer = question.choice_set.get(pk=choice_id)
			except (KeyError, Choice.DoesNotExist):
				return render(request, 'survey/survey.html',{'survey':survey,
                                                         'error_message': "Please fill out full survey befor submiting."})       
			else:
				question.answer = answer.choice_text
				question.save()
       
		if int(question.atype) == 2:
			choice_list = request.POST.getlist(str(question.id))
			choices = ""
			for choice_id in choice_list:
				try:
					answer = question.choice_set.get(pk=choice_id)
				except (KeyError, Choice.DoesNotExist):
					return render(request, 'survey/survey.html',{'survey':survey,
                                                         'error_message': "Please fill out full survey befor submiting."})       
				else:
					if choices:#checks to see if it is empty (empty sting is false)
						choices += "+"
						choices += answer.choice_text
					else:
						choices += answer.choice_text
			question.answer = str(choices.split("+"))
			question.save()
        
		if int(question.atype) == 0:
			question.answer = request.POST[str(question.id)]
			question.save()
	jsonData = serializers.serialize("json",survey.question_set.all())
	try:
		user = User.objects.get(phone_number = user_id)
		surveydata_object = SurveyData.objects.get(user = user)
		surveydata_string=surveydata_object.surveydata
		adddata = eval(str(surveydata_string))
		adddata[str(survey.id)]=str(jsonData)
		surveydata_object.surveydata = str(adddata)
		surveydata_object.save()
	except:
		import sys
		exc_type, exc_obj,exc_tb = sys.exc_info()
		print exc_type, exc_obj,exc_tb
		print 'Exception: Could not parse JSON'
		return HttpResponse('Fail')
	return HttpResponseRedirect(reverse('survey:results', args=(survey.id,)))

def results(request,survey_id):
    survey = get_object_or_404(Survey, pk = survey_id )
    return render(request,'survey/results.html',{'survey':survey})    
            
            
            
    
