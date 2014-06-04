'''
Created on May 23, 2014

@author: maxclapp
'''
from django.db import models
from django.utils import timezone

choices = {
           (0,"Short answer"),
           (1,"Multiple choice pick one"),
           (2,"Multiple choice pick all that apply"),
           }

class Survey(models.Model):
    title = models.CharField(max_length = 150)
    created_date = models.DateTimeField('Date to be given on',default = timezone.now())
    def __unicode__(self):
        return self.title

class Question(models.Model):
    atype = models.IntegerField("Answer type",choices = choices, default = 0)
    text = models.CharField("Question",max_length = 500)
    answer = models.CharField(max_length = 500,default = "0")
    survey = models.ForeignKey(Survey)
    def __unicode__(self):
        return self.text
    
class Choice(models.Model):
    question = models.ForeignKey(Question)
    choice_text = models.CharField(max_length=500)
    def __unicode__(self):
        return self.choice_text
    
