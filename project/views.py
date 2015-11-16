from django.shortcuts import render

from project.models import Question, QuestionOrder, Answer, SystemObject,AttributeValue, Attribute, \
    AttributeAnswer,RulesAttribute
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
        "counter": 0,
        "asked_questions": [],
        "chosed_answers": [],
        "applied_rules": [],
    }
    request.session = session

def question(request):
    init_session(request)
    counter = request.session.get('counter')
    question = Question.objects.filter(id=counter)
    answers = Answer.objects.filter(question = question)
    context = {
        'question': question,
        'answers': answers,
        'counter': counter
    }

    return render(request, 'question.html', context)

def answer(request):
    request.session.counter = request.session.get('counter')+1

def final(request):
    return 1


