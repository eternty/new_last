from django.contrib import admin
# Register your models here.
from django import forms
from .models import *
class AttributeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'main', 'get_defines_attribute')

class AttributeValueAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_attribute', 'value', 'ifselected')

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_question', 'type')

class SystemObjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

class ObjectsAttributeAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_sys_object', 'value')

class AnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_question', 'body')

class AttributeAnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_answer', 'get_value')

class RulesAttributeAdmin(admin.ModelAdmin):
    list_display = ('get_value1', 'get_value2', 'get_result')

class QuestionOrderAdmin(admin.ModelAdmin):
    list_display = ('get_answer', 'get_next', 'get_not_ask')

admin.site.register(Attribute, AttributeAdmin)
admin.site.register(AttributeValue, AttributeValueAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(SystemObject, SystemObjectAdmin)
admin.site.register(ObjectsAttribute, ObjectsAttributeAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(AttributeAnswer, AttributeAnswerAdmin)
admin.site.register(RulesAttribute, RulesAttributeAdmin)
admin.site.register(QuestionOrder, QuestionOrderAdmin)
