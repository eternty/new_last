from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User, AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import ugettext_lazy as _
# Create your models here.
class MyUserManager(BaseUserManager):

    def _create_user(self, username, email, password,
                     is_staff, is_superuser, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        now = timezone.now()
        email = self.normalize_email(email)
        user = self.model(username=username, email=email,
                          is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser, last_login=now,
                          date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email, password=None, **extra_fields):
        return self._create_user(username, email, password, False, False,
                                 **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        return self._create_user(username, email, password,
                                 True, True, **extra_fields)

class Attribute(models.Model):
    name = models.CharField(max_length = 50, verbose_name= u'Название')
    main = models.BooleanField(default=False, verbose_name=u'Атрибут')
    defines_attribute = models.ForeignKey("self", verbose_name=u'Определяет_атрибут')
    class Meta:
        db_table = "attribute"
        verbose_name = u"Атрибут"
        verbose_name_plural = u"Атрибуты"
    def __unicode__(self):
        return self.name

class AttributeValue(models.Model):
    attribute = models.ForeignKey(Attribute,on_delete=models.CASCADE, verbose_name = u'Атрибут')
    attribute_value = models.CharField(max_length=50, verbose_name=u'Значение')
    selected = models.BooleanField(default=False)
    class Meta:
        db_table = "attribute_value"
        verbose_name = u"Значение атрибута"
        verbose_name_plural = u"Значения атрибутов"
    def __unicode__(self):
        return str(self.id) + ". " + self.attribute.name + " : " + self.attribute_value

class ObjectsAttribute(models.Model):
    sys_object = models.ForeignKey(SysObject)
    value = models.ForeignKey(AttributeValue)
    class Meta:
        db_table = "objects_attribute"
        verbose_name = u"Атрибут объекта"
        verbose_name_plural = u"Атрибуты объектов"


class SysObject(models.Model):
    name = models.TextField(verbose_name= u'Название')
    attributes = models.ManyToManyField (AttributeValue, through='ObjectsAttribute',
                                         through_fields= ('sys_object','attribute_value'),
                                         null=True, blank=True, verbose_name= u'Атрибуты')
    class Meta:
        db_table = "object"
        verbose_name = u"Объект"
        verbose_name_plural = u"Объекты"
    def __unicode__(self):
        return self.name

class Question(models.Model):
    SELECT = 0
    NUMBER = 1
    CHOICES = (
        (SELECT, "Выберете ответ"),
        (NUMBER, "Напишите число"),

    )
    text = models.CharField(verbose_name=u'Teкст')
    type = models.IntegerField(choices=CHOICES, verbose_name=u'Тип')

    class Meta:
        db_table = "question"
        verbose_name = u"Вопрос"
        verbose_name_plural = u"Вопросы"

    def __unicode__(self):
        return u"Вопрос № " + self.id + self.text      #perhaps I should use unicode(self.id)

class Answer(models.Model):
    question = models.ForeignKey(Question, related_name='answers',on_delete=models.CASCADE,
                                 verbose_name=u'Вопрос')
    body = models.TextField(verbose_name=u'Текст')

    class Meta:
        db_table = "answer"
        verbose_name = u"Ответ"
        verbose_name_plural = u"Ответы"

    def __unicode__(self):
        return u"Ответ №" + self.id + u" на вопрос №" + self.question.id

class AttributeAnswer(models.Model):
    answer = models.ForeignKey(Answer, verbose_name=u'Ответ')
    attribute_value = models.ForeignKey(AttributeValue, verbose_name=u'Значение атрибута')

    class Meta:
        db_table = "attribute_value"
        verbose_name = u"Ответ-атрибут"
        verbose_name_plural = u"Ответы и атрибуты"

    def __unicode__(self):
        return u"Ответ #" + self.answer.body + u" # на вопрос #" + self.answer.question.text +\
               u"определяет значение атрибута " + self.attribute_value.attribute.name + u" как "\
               + self.attribute_value.attribute_value
class Rules_Attribute(models.Model):
    and_rule = 0
    or_rule = 1
    CHOICES = (
        (and_rule, "И"),
        (or_rule, "ИЛИ"),

    )
    value1 = models.ForeignKey(AttributeValue, verbose_name=u'Условие 1')
    value2 = models.ForeignKey(AttributeValue, verbose_name=u'Условие 2')
    result = models.ForeignKey(AttributeValue, verbose_name=u'Результат')
    rule = models.IntegerField(choices=CHOICES, verbose_name=u'Операция')
    class Meta:
        db_table = "rules_attr"
        verbose_name = u"Правило атрибутов"
        verbose_name_plural = u"Правила атрибутов"

    def __unicode__(self):
        return self.value1.attribute_value + str(self.rule) + self.value2.attribute_value + u" = " + \
               self.result.attribute_value

#class Question_Order
