from django.shortcuts import render
from project.models import Question, QuestionOrder, Answer, SystemObject, AttributeValue, Attribute, \
    AttributeAnswer, RulesAttribute, ObjectsAttribute
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
              #we add all variants as keys
        final_variant = aim_variants[0]
        for aim_variant in aim_variants:
            if attributes_tocount.count(aim_variant)>attributes_tocount.count(final_variant):
                final_variant = aim_variant
        chosed_attributes.append(final_variant)

    all_objects = SystemObject.objects.all()

    for one_object in all_objects:
        his_attr_container = ObjectsAttribute.objects.filter(sys_object=one_object)
        his_attr_count = 0
        for one_containing in his_attr_container:
            if one_containing.value in chosed_attributes:
                his_attr_count += 1
        one_object.count = his_attr_count

    final_object = all_objects[0]
    for object1 in all_objects:
        if object1.count>final_object.count:
            final_object = object1
    context = {
         'chosed_answers': chosed_answers,
         'chosed_attributes': chosed_attributes,
         'attributes_tocount': attributes_tocount,
         'all_objects': all_objects,
         'final_object': final_object
    }


    return render(request,'result.html', context)

def final(request):

    return render(request,'final.html')

def vera(request):
    global choice
    main_attributes = []
    for chosed_answer in chosed_answers:              #here we get attributes from answers!
        selected_attributes = AttributeAnswer.objects.filter(answer=chosed_answer)
        for sel_attr in selected_attributes:
            chosed_attributes.append(sel_attr.attribute_value)
            if sel_attr.attribute_value.attribute.main==True:
                main_attributes.append(sel_attr.attribute_value)
    #then we should find out attributes from other attributes
    rules_attributes = RulesAttribute.objects.all()
    attributes_tocount=[]     # these are values of attributes, which are matter for define the attribute like object
    #counting_attributes = [] # attributes, which has a set of defifnitions, example: dosha
    for rule in rules_attributes:
        if rule.rule==0:                 #and_rule - all the conditons must be achieved
            if rule.value1 in chosed_attributes:
                if rule.value2 in chosed_attributes:
                    chosed_attributes.append(rule.result)
                    if rule.result.attribute.main:
                        main_attributes.append(rule.result)
                    chosed_attributes.remove(rule.value1)
                    chosed_attributes.remove(rule.value2)
        if rule.rule==1:
            if rule.value1 in chosed_attributes:
                chosed_attributes.append(rule.result)
                if rule.result.attribute.main:
                        main_attributes.append(rule.result)
                chosed_attributes.remove(rule.value1)
                rules_attributes.exclude(result=rule.result)
                if rule.value1 in chosed_attributes:
                    chosed_attributes.remove(rule.value2)

            if rule.value2 in chosed_attributes:
                chosed_attributes.append(rule.result)
                if rule.result.attribute.main:
                        main_attributes.append(rule.result)
                if rule.value1 in chosed_attributes:
                    chosed_attributes.remove(rule.value1)
                chosed_attributes.remove(rule.value2)
                rules_attributes.exclude(result=rule.result)
        else:
            if rule.value1 in chosed_attributes:
                if rule.result.attribute.like_object:
                    attributes_tocount.append(rule.result)        #we add here all attrib_values into special list
                else:
                    chosed_attributes.append(rule.result)
                    if rule.result.attribute.main:
                        main_attributes.append(rule.result)


    aim_attributes = Attribute.objects.filter(like_object=True)

    for aim_attribute in aim_attributes:
        aim_variants = AttributeValue.objects.filter(attribute = aim_attribute)
              #we add all variants as keys
        final_variant = aim_variants[0]
        for aim_variant in aim_variants:
            if attributes_tocount.count(aim_variant)>attributes_tocount.count(final_variant):
                final_variant = aim_variant
        chosed_attributes.append(final_variant)
        if rule.result.attribute.main:
            main_attributes.append(rule.result)


    all_objects = SystemObject.objects.all()
    amount = all_objects.count()
    for one_object in all_objects:           #this is apriori probability!
        one_object.count = 1/amount

    attr_lines = ObjectsAttribute.objects.all()
    for main_attribut in main_attributes:            #at first we check, whether chosed_attribute means smth to us!
        for attr_line in attr_lines:
            if main_attribut == attr_line.value:
                for main_attribute in main_attributes:     # for every chosed_attribute we will count the probability
                    znamen = 0                                 # we count znamenatel` for Bayes` formula
                    current_att_lines = ObjectsAttribute.objects.filter(value=main_attribute)   # we take all lines in the table, lines related to the chosed_atr

                    for one_object in all_objects:            # it is for znamenatel`
                        curr_probability = 0
                        for att_line in current_att_lines:   # here we get probability to one_object and chosed_attribute, if it exists! otherway we have 0!
                            if one_object == att_line.sys_object:
                                curr_probability = att_line.probability
                                znamen += one_object.count*curr_probability
                    if znamen > 0:
                        for object1 in all_objects:
                            curr_probability = 0
                            for attrib_line in current_att_lines:   # here we get probability to one_object and chosed_attribute, if it exists! otherway we have 0!
                                if object1 == attrib_line.sys_object:
                                    curr_probability = attrib_line.probability
                            chislit = curr_probability * object1.count
                            object1.count = (chislit/znamen)

    final_object = all_objects[0]
    for onen_object in all_objects:
        if onen_object.count > final_object.count:
            final_object = onen_object

    '''for one_object2 in all_objects:           #normalization
        if one_object2!=final_object:
            one_object2.count /= final_object.count
    final_object.count = 1'''

    context = {
         'chosed_answers': chosed_answers,
         'chosed_attributes': chosed_attributes,
         'attributes_tocount': attributes_tocount,
         'all_objects': all_objects,
         'final_object': final_object
    }


    return render(request,'result.html', context)

def vera_i_razum(request):
    global choice
    main_attributes = []
    for chosed_answer in chosed_answers:              #here we get attributes from answers!
        selected_attributes = AttributeAnswer.objects.filter(answer=chosed_answer)
        for sel_attr in selected_attributes:
            chosed_attributes.append(sel_attr.attribute_value)
            if sel_attr.attribute_value.attribute.main==True:
                main_attributes.append(sel_attr.attribute_value)
    #then we should find out attributes from other attributes
    rules_attributes = RulesAttribute.objects.all()
    attributes_tocount=[]     # these are values of attributes, which are matter for define the attribute like object
    #counting_attributes = [] # attributes, which has a set of defifnitions, example: dosha
    for rule in rules_attributes:
        if rule.rule==0:                 #and_rule - all the conditons must be achieved
            if rule.value1 in chosed_attributes:
                if rule.value2 in chosed_attributes:
                    chosed_attributes.append(rule.result)
                    if rule.result.attribute.main:
                        main_attributes.append(rule.result)
                    chosed_attributes.remove(rule.value1)
                    chosed_attributes.remove(rule.value2)
        if rule.rule==1:
            if rule.value1 in chosed_attributes:
                chosed_attributes.append(rule.result)
                if rule.result.attribute.main:
                        main_attributes.append(rule.result)
                chosed_attributes.remove(rule.value1)
                rules_attributes.exclude(result=rule.result)
                if rule.value1 in chosed_attributes:
                    chosed_attributes.remove(rule.value2)

            if rule.value2 in chosed_attributes:
                chosed_attributes.append(rule.result)
                if rule.result.attribute.main:
                        main_attributes.append(rule.result)
                if rule.value1 in chosed_attributes:
                    chosed_attributes.remove(rule.value1)
                chosed_attributes.remove(rule.value2)
                rules_attributes.exclude(result=rule.result)
        else:
            if rule.value1 in chosed_attributes:
                if rule.result.attribute.like_object:
                    attributes_tocount.append(rule.result)        #we add here all attrib_values into special list
                else:
                    chosed_attributes.append(rule.result)
                    if rule.result.attribute.main:
                        main_attributes.append(rule.result)


    all_objects = SystemObject.objects.all()
    amount = all_objects.count()
    for one_object in all_objects:                                   #this is apriori probability!
        one_object.count = 1/amount

    #unclear logic for attributes like object!

    aim_attributes = Attribute.objects.filter(like_object=True)      # here we change measure of attributes like object!
    for aim_attribute in aim_attributes:                     #ex Dosha!
        amount_in_count = 0
        for count1 in attributes_tocount:
            if count1.attribute == aim_attribute:          # how much doshas value are matter
                amount_in_count += 1
        aim_variants = AttributeValue.objects.filter(attribute=aim_attribute)       #let`s see for every attrib/value
        probabil_tochange_lines = ObjectsAttribute.objects.filter(value__attribute=aim_attribute) #all lines for the attribute, not to exact attr_value!

        for aim_variant1 in aim_variants:
            var_amount = attributes_tocount.count(aim_variant1)
            aim_variant1.measure = var_amount/amount_in_count            #we know the measure of attr/value

            znamenat = 0
            for one_object23 in all_objects:            # it is for znamenatel`
                curr_probability1 = 0
                for attrib1_line in probabil_tochange_lines:   # here we get probability to one_object and chosed_attribute, if it exists! otherway we have 0!
                    if attrib1_line.value == aim_variant1:
                        if one_object23 == attrib1_line.sys_object:
                            curr_probability1 = attrib1_line.probability * aim_variant1.measure
                            znamenat += one_object23.count*curr_probability1
            if znamenat>0:
                for object17 in all_objects:
                    curr_probability2 = 0
                    for attrib12_line in probabil_tochange_lines:   # here we get probability to one_object and chosed_attribute, if it exists! otherway we have 0!
                        if attrib12_line.value == aim_variant1:
                            if object17 == attrib12_line.sys_object:
                                curr_probability2 = attrib12_line.probability * aim_variant1.measure
                    chislit1 = curr_probability2 * object17.count
                    object17.count = (chislit1/znamenat)


    # this is for main_attributes

    attr_lines = ObjectsAttribute.objects.all()
    for main_attribut in main_attributes:            #at first we check, whether chosed_attribute means smth to us!
        for attr_line in attr_lines:
            if main_attribut == attr_line.value:
                for main_attribute in main_attributes:     # for every chosed_attribute we will count the probability
                    znamen = 0                                 # we count znamenatel` for Bayes` formula
                    current_att_lines = ObjectsAttribute.objects.filter(value=main_attribute)   # we take all lines in the table, lines related to the chosed_atr

                    for one_object32 in all_objects:            # it is for znamenatel`
                        curr_probability = 0
                        for att_line in current_att_lines:   # here we get probability to one_object and chosed_attribute, if it exists! otherway we have 0!
                            if one_object32 == att_line.sys_object:
                                curr_probability = att_line.probability
                                znamen += one_object32.count*curr_probability
                    if znamen>0:
                        for object18 in all_objects:
                            curr_probability = 0
                            for attrib_line in current_att_lines:   # here we get probability to one_object and chosed_attribute, if it exists! otherway we have 0!
                                if object18 == attrib_line.sys_object:
                                    curr_probability = attrib_line.probability
                            chislit = curr_probability * object18.count
                            object18.count = (chislit/znamen)

    final_object = all_objects[0]
    for onen_object in all_objects:
        if onen_object.count > final_object.count:
            final_object = onen_object

    '''for one_object2 in all_objects:           #normalization
        if one_object2!=final_object:
            one_object2.count /= final_object.count
    final_object.count = 1'''

    context = {
         'chosed_answers': chosed_answers,
         'chosed_attributes': chosed_attributes,
         'attributes_tocount': attributes_tocount,
         'all_objects': all_objects,
         'final_object': final_object
    }


    return render(request,'result.html', context)

