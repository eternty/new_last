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
        "asked_questions": [],
        "chosed_answers": [],
        "applied_rules": [],
    }
    request.session = session

def update_sessions(request,inc_questions = False,finished=False, write_results=False, results = "" ):
    if inc_questions:
        request.session['history']['questions'] += 1
    if write_results:
        request.session['history']['results'] = results
    if finished:
def questions(request):
    session = request.session
    answers = []
    if session.
    questions = Question.objects.get(all()),
    context = {


    }
    if request.method == 'GET':

    elif request.method == 'POST':


