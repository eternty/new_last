from django.contrib import admin
# Register your models here.
from django import forms
from .models import *
class AttributeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'main', 'defines_attribute', 'like_object')

class AttributeValueAdmin(admin.ModelAdmin):
    list_display = ('id', 'attribute', 'value', 'ifselected', 'measure')

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'type','if_first')

class SystemObjectForm(forms.ModelForm):
    attributes = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple(),
                                                queryset=AttributeValue.objects.filter(attribute__main=True))
class SystemObjectAdmin(admin.ModelAdmin):
    form = SystemObjectForm

class ObjectsAttributeAdmin(admin.ModelAdmin):
    list_display = ('id', 'sys_object', 'value', 'probability')

class AnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'body')

class AttributeAnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'answer', 'attribute_value')

class RulesAttributeAdmin(admin.ModelAdmin):
    list_display = ('value1', 'value2', 'result', 'rule')

class QuestionOrderAdmin(admin.ModelAdmin):
    list_display = ('answer', 'next', 'not_ask')

admin.site.register(Attribute, AttributeAdmin)
admin.site.register(AttributeValue, AttributeValueAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(SystemObject, SystemObjectAdmin)
admin.site.register(ObjectsAttribute, ObjectsAttributeAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(AttributeAnswer, AttributeAnswerAdmin)
admin.site.register(RulesAttribute, RulesAttributeAdmin)
admin.site.register(QuestionOrder, QuestionOrderAdmin)

