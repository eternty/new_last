from django.shortcuts import render
from project.models import Question, QuestionOrder, Answer, SystemObject, AttributeValue, Attribute, \
    AttributeAnswer, RulesAttribute


# Create your views here.
def index(request):
    session = request.session

    args = {}
    if session.get('b') == 'b':
        args['test'] = u'Снова'
    else:
        session['b'] = 'b'

    return render(request, 'index.html', args)


def init_session(request):
    session = {
        "chosed_answers": [],
        "applied_rules": [],
    }
    request.session = session


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
        'counter': counter
    }
    #request.session['asked_questions'].append(question)
    return render(request, 'question.html', context)

def defining_attributes(request,answer):
    request.session

def answer(request):
    got_answer = request.POST.get("answer")
    '''request.session["chosed_answers"].append(got_answer)'''
    question_answer = QuestionOrder.objects.get(answer=got_answer)
    #answer_attribute = AttributeAnswer.objects.filter(answer_id=got_answer)
    question = question_answer.next
    if question.text=='end':
        return render(request, 'final.html')
    answers = Answer.objects.filter(question=question)
    '''counter = request.session["counter"] + 1'''
    context = {
            'question': question,
            'answers': answers,
       #    'counter': counter
            }
    return render(request, 'question.html', context)

def final(request):

    return render(request, 'final.html')
