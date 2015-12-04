from django.shortcuts import render
from project.models import Question, QuestionOrder, Answer, SystemObject, AttributeValue, Attribute, \
    AttributeAnswer, RulesAttribute
from django.db.models import Count
import json

# Create your views here.
SESSION_KEY = "ExpertSystem"
def index(request):
    session = request.session

    args = {}
    if session.get('b') == 'b':
        args['test'] = u'Снова'
    else:
        session['b'] = 'b'

    return render(request, 'index.html', args)


chosed_answers = []
chosed_attributes = []

def question(request):
    init_session(request)

    counter = request.session.get('counter')
    first_questions = Question.objects.filter(if_first=True)
    ordered = first_questions.order_by("id")
    question = ordered[0]

    answers = Answer.objects.filter(question=question)
    context = {
        'question': question,
        'answers': answers,
        'counter': counter,
    }
    #request.session['asked_questions'].append(question)
    return render(request, 'question.html', context)

def answer(request):
    got_answer = request.POST.get("answer")
    '''request.session["chosed_answers"].append(got_answer)'''
    question_answer = QuestionOrder.objects.get(answer=got_answer)
    chosed_answer = Answer.objects.get(id= got_answer)
    chosed_answers.append(chosed_answer)
    question = question_answer.next
    if question.text=='end':
        return render(request, 'final.html')
    answers = Answer.objects.filter(question=question)
    '''counter = request.session["counter"] + 1'''
    context = {
            'question': question,
            'answers': answers,
            }
    return render(request, 'question.html', context)

def init_session(request):
    sys_objects = SystemObject.objects.all()
    objects = []
    for object in sys_objects:
        objects.append(
            {
                "name": object.name,
                "weight":0,
            }
        )
    session = {
        "chosed_answers": [],
        #"asked_questions": [],
        #"applied_attr_rules": [],
        "objects": objects,
        "selected_attributes": {}
    }
    request.session[SESSION_KEY] = session

def add_to_session(request, chosed_answers = None, selected_attributes = None ):
    session = request.session.get(SESSION_KEY)
    if chosed_answers:
        session["chosed_answers"] = chosed_answers

    if selected_attributes:
        session["selected_params"] = selected_attributes

    request.session[SESSION_KEY] = session

def clear_session(request):
    if SESSION_KEY in request.session:
        del request.session[SESSION_KEY]

def defining_attributes():
    #at first we should recognise the attributes right from answers
    global choice
    for chosed_answer in chosed_answers:
        selected_attributes = AttributeAnswer.objects.filter(answer=chosed_answer)
        for sel_attr in selected_attributes:
            chosed_attributes.append(sel_attr.attribute_value)
    #then we should find out attributes from other attributes
    rules_attributes = RulesAttribute.objects.all()
    #rules_attributes.order_by(id)
    for rule in rules_attributes:
        if rule.value1 in chosed_attributes:
            if rule.value2 in chosed_attributes:
                if rule.result.attribute == rule.value1.attribute:
                    chosed_attributes.remove(rule.value1)
                if rule.result.attribute == rule.value2.attribute:
                    chosed_attributes.remove(rule.value2)
                chosed_attributes.append(rule.result)
            if rule.value2 == None:
                aim_attribute = Attribute.objects.get(attribute=rule.result.attribute)    #define aim attr
                choices = AttributeValue.objects.filter(attribute=aim_attribute)          #select its attrib_values
                result_choices = []
                for choice in choices:
                    result_choices.append([choice])
                    match_rules = RulesAttribute.objects.filter(result=choice)
                    for match_rule in match_rules:
                        if match_rule.value1 in chosed_attributes:
                            result_choices[choice].append(match_rule.value1)
                            rules_attributes.exclude(match_rule)
                result_choices.sort([choice].__len__())
                chosed_attributes.append(result_choices[0])
    context = {
         'chosed_answers': chosed_answers,
         'chosed_attributes': chosed_attributes
    }
    return render('result.html', context)

#def defining_():

def result(request):
    global choice
    for chosed_answer in chosed_answers:              #here we get attributes from answers!
        selected_attributes = AttributeAnswer.objects.filter(answer=chosed_answer)
        for sel_attr in selected_attributes:
            chosed_attributes.append(sel_attr.attribute_value)
    #then we should find out attributes from other attributes
    rules_attributes = RulesAttribute.objects.all()
    attributes_tocount=[]     # these are values of attributes, which are matter for define the attribute like object
    counting_attributes = [] # attributes, which has a set of defifnitions, example: dosha
    for rule in rules_attributes:
        if rule.rule==0:                 #and_rule - all the conditons must be achieved
            if rule.value1 in chosed_attributes:
                if rule.value2 in chosed_attributes:
                    chosed_attributes.append(rule.result)
                    chosed_attributes.remove(rule.value1)
                    chosed_attributes.remove(rule.value2)
        if rule.rule==1:
            if rule.value1 in chosed_attributes:
                chosed_attributes.append(rule.result)
                chosed_attributes.remove(rule.value1)
                rules_attributes.exclude(result=rule.result)
                if rule.value1 in chosed_attributes:
                    chosed_attributes.remove(rule.value2)

            if rule.value2 in chosed_attributes:
                chosed_attributes.append(rule.result)
                if rule.value1 in chosed_attributes:
                    chosed_attributes.remove(rule.value1)
                chosed_attributes.remove(rule.value2)
                rules_attributes.exclude(result=rule.result)
        else:
            if rule.value1 in chosed_attributes:
                if rule.result.attribute.like_object == True:
                    attributes_tocount.append(rule.result)        #we add here all attrib_values into special list
                else:
                    chosed_attributes.append(rule.result)

    aim_attributes = Attribute.objects.filter(like_object=True)
    for aim_attribute in aim_attributes:
        aim_variants = AttributeValue.objects.filter(attribute = aim_attribute)
        for aim_variant in aim_variants:
            for attrib_tocount in attributes_tocount:
                if aim_variant.value==attrib_tocount.value:
                    aim_variant.count = aim_variant.count +1
        aim_variants.order_by('-count').reverse()

        chosed_attributes.append(aim_variants[0])

    '''for attr_to_count in  attributes_tocount:   #we have to count includings and choose the large one
        aim_attribute = Attribute.objects.get(attribute=attr_to_count.attribute)
        aim_variants = AttributeValue.objects.filter(attribute = aim_attribute)

        attr_to_count.count = attr_to_count.count + 1
        if attr_to_count.attribute not in counting_attributes:
            counting_attributes.append(attr_to_count.attribute)   # we save attributes, which are defining by count of appearings

    for counting_attribute in counting_attributes:  # now all those attributes, who are waiting to be defined
        set_of_attributes = AttributeValue.objects.filter(attribute= counting_attribute).order_by('count').reverse()
        chosed_attributes.append(set_of_attributes[0])
        '''

   #add the count of doshas

    context = {
         'chosed_answers': chosed_answers,
         'chosed_attributes': chosed_attributes,
         'attributes_tocount':attributes_tocount,

    }
    return render(request,'result.html', context)

def final(request):

    return render(request,'final.html')


