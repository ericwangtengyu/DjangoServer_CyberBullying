
'''
Created on May 23, 2014

@author: maxclapp
'''
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect,HttpResponse
from django.shortcuts import get_object_or_404,render
from django.core import serializers
from .models import Survey, Question,Choice
from DataCollection.models import User, SurveyData, UpdatedDate
from django.core.mail import send_mail
import json
import subprocess


def refresh(request):
    subprocess.call(['java','-jar','/home/clapp/Documents/DataCollectionJava/server-side-collection/collectAllData.jar'])
    return HttpResponse("Updateing facebook ")

def survey(request , survey_id , user_id):
    user = get_object_or_404(User, pk = user_id )
    date = get_object_or_404(UpdatedDate, user = user )
    survey = get_object_or_404(Survey, pk = survey_id )
    return render(request , 'survey/survey.html',{'survey':survey,'user_id':user_id, 'date':date})
    
def sendemail(request,survey_id,user_id):
    text = request.POST["textbox"]
    text = text + "\n \n user_id " + str(user_id) + "\n \nsurvey_id " + str(survey_id)
    send_mail("DATA ERROR" ,text,"cyber-bullying@uiowa.edu",["llclaptrapll@gmail.com"])
    return HttpResponse("Thank you problem will be taken care of asap")

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
    qs = survey.question_set.filter(answer = "No")
    if qs:
        return HttpResponseRedirect(reverse('survey:email', args=(survey.id,user_id)))
    try:
        user = User.objects.get(phone_number = user_id)
        surveydata_object = SurveyData.objects.get(user = user)
        surveydata_string=surveydata_object.surveydata
        adddata = eval(str(surveydata_string))
        adddata[str(survey.id)]=str(jsonData)
        surveydata_object.surveydata = str(adddata)
        surveydata_object.save()
    except:
        import traceback
        exception = traceback.format_exc()
        print exception
        send_mail("DATA ERROR" ,exception,"cyber-bullying@uiowa.edu",["llclaptrapll@gmail.com"])
        return render(request,'DataCollection/fail.html')
    return HttpResponseRedirect(reverse('survey:results', args=(survey.id,)))

def results(request,survey_id):
    survey = get_object_or_404(Survey, pk = survey_id )
    return render(request,'survey/results.html',{'survey':survey})    
            
def email(request,survey_id,user_id):
    return render(request,'survey/email.html',{'survey_id':survey_id,
                                                "user_id":user_id})    
