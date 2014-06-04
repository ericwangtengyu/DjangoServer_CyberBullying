'''
Created on May 28, 2014

@author: maxclapp
'''
# from django import forms
# from django.forms.models import inlineformset_factory
# from servey.models import Servey,SingleChoiceQuestion,Choice
#       
# class singleQuestionForm(forms.Form):
#     def __init__(self,*args,**kwargs):
#         choices = kwargs.pop('my_choices')
#         super(singleQuestionForm,self).__init__(*args, **kwargs)
#         self.fields['answer'] = forms.Select(choices = choices)
#     text = forms.CharField()