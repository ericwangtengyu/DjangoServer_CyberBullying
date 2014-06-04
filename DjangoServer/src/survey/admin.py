'''
Created on May 29, 2014

@author: maxclapp
'''
from django.contrib import admin
from django import forms

from survey.models import Survey,Question,Choice

CONTENT_HELP_TEXT = ' '.join(['<p>Only add choices for',
                              '<strong>Multiple Choice</strong>',
                              'questions not short answer.',
                              'If more choices are needed just press',
                              'the add another choice button in lower left',
                              'corner.<br/>'])

class ChoiceInline(admin.StackedInline):
    model = Choice
    fieldsets = [
                 (None,{
                             'fields':('choice_text',),
                             'description': '<div class="help">%s</div>' % CONTENT_HELP_TEXT,}),
                 ]
    extra = 1

class QuestionForm(admin.ModelAdmin):
    fields = ('survey','text','atype')
    radio_fields = {'atype': admin.VERTICAL }
    inlines = [
               ChoiceInline,
               ]

admin.site.register(Survey)
admin.site.register(Choice)
admin.site.register(Question,QuestionForm)
    
