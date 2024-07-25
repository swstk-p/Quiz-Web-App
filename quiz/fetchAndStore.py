import urllib.request, urllib.parse, urllib.error
import ssl
import json

from django.db import IntegrityError
from .models import *

def fetchQ(api, api2):
    # recursion termination
    if api is None:return None

    try:
        # hitting url(api)
        with urllib.request.urlopen(api) as hit:

            try:
                # storing questions from api
                questions=json.loads(hit.read().decode())
            except:
                # backup api in case of failure
                questions=fetchQ(api2, None)
    except:
        questions=fetchQ(api2, None)

    # returning questions
    return questions

def parseQ(questions,qnsNum):

    i=0

    while i<qnsNum:

        # parsing useful bits
        cat = questions[i]["category"].strip().lower()
        ans = questions[i]["correctAnswer"].strip()
        opts = questions[i]["incorrectAnswers"]

        if type(questions[i]["question"]) is dict:
            que = questions[i]["question"]["text"].strip()
        else:
            que = questions[i]["question"].strip()

        diff = questions[i]["difficulty"].strip()

        #returning the parsed bits
        yield (cat, diff, opts, ans, que)

        #incrementing counter for generator
        i+=1



def storeDifficulty(diff, getDiff):
    d = Difficulties(level=diff)
    saved=False

    try:
        d.save()
        saved=True
    except IntegrityError as e:
        pass

    if getDiff:
        if saved:
            return d

        difficulty = Difficulties.objects.get(level=diff)
        return difficulty

def storeFormat(format, getFormat):
    f = Formats(format=format)
    saved=False

    try:
        f.save()
        saved=True
    except IntegrityError as e:
        pass

    if getFormat:
        if saved:
            return f

        ret_format = Formats.objects.get(format=format)
        return ret_format

def storeCategory(category, getCat):
    c=Categories(category=category.strip().lower().replace(' ',"_"))
    saved=False

    try:
        c.save()
        saved=True
    except IntegrityError as e:
        pass

    if getCat:
        if saved:
            return c

        cat=Categories.objects.get(category=category)
        return cat

def storeQA(diff, cat, options, answer, question, getAns, getQns):
    #saving options
    for opt in options:
        o = Answers(answer=opt, question=None)
        o.save()

    #saving the answer
    a=Answers(answer=answer, question=None)
    a.save()

    q_saved=False

    #saving the question
    try:
        q=Questions(question=question, answer=a, difficulty=diff, category=cat, priority=20, asked=0, answered=0)
        q.save()
        q_saved=True
    except IntegrityError as e:
        pass

    #updating the answers and options
    if q_saved:
        Answers.objects.filter(question=None).update(question=q)
    else:
        Answers.objects.filter(question=None).delete()

    #obtaining question
    qns=Questions.objects.get(question=question)

    #returning IDs if required
    if getAns and getQns:
        return(a, qns)

    if getAns:
        return a

    if getQns:
        return qns

def pullStoreFromAPI():
    (api1, api2) = getAPI()

    questions=fetchQ(api1, api2)

    if questions is not None:
        for category, difficulty, options, answer, question in parseQ(questions, len(questions)):

            cat=storeCategory(category, True)
            diff=storeDifficulty(difficulty, True)

            storeQA(diff, cat, options, answer, question, False, False)

def getAPI():

    api2="https://the-trivia-api.com/api/questions"
    api="https://the-trivia-api.com/v2/questions"

    return(api, api2)