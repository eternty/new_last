from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User, AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import ugettext_lazy as _

from django.utils.translation import ugettext_lazy as _
# Create your models here.
class Attribute(models.Model):
    name = models.CharField(max_length = 60, verbose_name= u'Название')
    main = models.BooleanField(default=False, verbose_name=u'Атрибут')
    like_object = models.BooleanField(default=False, verbose_name=u'Подсчет совпадений')
    defines_attribute = models.ForeignKey("self", verbose_name=u'Определяет_атрибут', blank=True, null=True)
    class Meta:
        db_table = "attribute"
        verbose_name = u"Атрибут"
        verbose_name_plural = u"Атрибуты"
    def get_defines_attribute(self):
        return self.defines_attribute.name
    def __str__(self):
        return self.name

class AttributeValue(models.Model):
    attribute = models.ForeignKey(Attribute,on_delete=models.CASCADE, verbose_name = u'Атрибут')
    value = models.CharField(max_length=50, verbose_name=u'Значение')
    ifselected = models.BooleanField(default=False)
    class Meta:
        db_table = "attribute_value"
        verbose_name = u"Значение атрибута"
        verbose_name_plural = u"Значения атрибутов"
    def get_attribute(self):
        return self.attribute.name
    def __str__(self):
        return self.value
    '''def __unicode__(self):
        return str(self.id) + ". " + self.attribute.name + " : " + str(self.value)'''

class SystemObject(models.Model):
    name = models.TextField(verbose_name=u'Название')
    attributes = models.ManyToManyField(AttributeValue, through='ObjectsAttribute',
                                         through_fields=('sys_object','value'),
                                         blank=True, verbose_name=u'Атрибуты')

    class Meta:
        db_table = "object"
        verbose_name = u"Объект"
        verbose_name_plural = u"Объекты"

    def __str__(self):
        return self.name

class ObjectsAttribute(models.Model):
    sys_object = models.ForeignKey(SystemObject)
    value = models.ForeignKey(AttributeValue)
    class Meta:
        db_table = "objects_attributes"
        verbose_name = u"Атрибут объекта"
        verbose_name_plural = u"Атрибуты объектов"
    def get_sys_object(self):
        return self.sys_object.name

class Question(models.Model):
    def __str__(self):
        return self.text
    SELECT = 0
    NUMBER = 1
    CHOICES = (
        (SELECT, "Выберете ответ"),
        (NUMBER, "Напишите число"),

    )
    text = models.CharField(verbose_name=u'Teкст', max_length=250)
    type = models.IntegerField(choices=CHOICES, verbose_name=u'Тип')
    if_first = models.BooleanField(default=False)
    class Meta:
        db_table = "question"
        verbose_name = u"Вопрос"
        verbose_name_plural = u"Вопросы"

    def get_question(self):
        return self.text

    '''def __unicode__(self):
        return u"Вопрос № " + str(self.id) + self.text      #perhaps I should use unicode(self.id)'''

class Answer(models.Model):
    question = models.ForeignKey(Question, related_name='answers',on_delete=models.CASCADE,
                                 verbose_name=u'Вопрос')
    body = models.TextField(verbose_name=u'Текст')

    class Meta:
        db_table = "answer"
        verbose_name = u"Ответ"
        verbose_name_plural = u"Ответы"
    def get_question(self):
        return self.question.text
    def get_answer(self):
        return self.body
    def __str__(self):
        return self.question.text + self.body
    '''def __unicode__(self):
        return u("Ответ №" + str(self.id) + " на вопрос №" + str(self.question.id))'''

class AttributeAnswer(models.Model):
    answer = models.ForeignKey(Answer, verbose_name=u'Ответ')
    attribute_value = models.ForeignKey(AttributeValue, verbose_name=u'Значение атрибута')
    def get_value(self):
        return self.attribute_value.value
    def get_answer(self):
        return self.answer.body
    class Meta:
        db_table = "attribute_answer"
        verbose_name = u"Ответ-атрибут"
        verbose_name_plural = u"Ответы и атрибуты"

    def __str__(self):
        return u"Ответ #" + self.answer.body + u" # на вопрос #" + self.answer.question.text +\
               u"определяет значение атрибута " + self.attribute_value.attribute.name + u" как "\
               + self.attribute_value.value

class RulesAttribute(models.Model):
    and_rule = 0
    or_rule = 1
    CHOICES = (
        (and_rule, "И"),
        (or_rule, "ИЛИ"),
    )
    value1 = models.ForeignKey(AttributeValue, verbose_name=u'Условие 1', related_name=u'value1')
    value2 = models.ForeignKey(AttributeValue, verbose_name=u'Условие 2', related_name=u'value2')
    result = models.ForeignKey(AttributeValue, verbose_name=u'Результат', related_name=u'result')
    rule = models.IntegerField(choices=CHOICES, verbose_name=u'Операция')
    def get_value1(self):
        return self.value1.value
    def get_value2(self):
        return self.value2.value
    def get_result(self):
        return self.result.value

    class Meta:
        db_table = "rules_attr"
        verbose_name = u"Правило атрибутов"
        verbose_name_plural = u"Правила атрибутов"

    '''def __unicode__(self):
        return self.value1.value + str(self.rule) + self.value2.value + u" = " + \
               self.result.value'''

class QuestionOrder(models.Model):
    answer = models.ForeignKey(Answer, verbose_name=u'Выбранный ответ-условие')
    next = models.ForeignKey(Question, verbose_name=u'Следующий вопрос', related_name=u'next')
    not_ask = models.ForeignKey(Question, verbose_name=u'Не спрашивать', related_name=u'not_ask', blank=True, null=True)
    class Meta:
        db_table = "question_order"
        verbose_name = u"Следующий вопрос"
        verbose_name_plural = u"Следующие вопросы"
    def get_answer(self):
        return self.answer.body
    def get_next(self):
        return self.next.text
    def get_not_ask(self):
        return self.not_ask.text




