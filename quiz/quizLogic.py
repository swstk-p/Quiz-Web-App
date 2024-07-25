from django.db import IntegrityError
from django.db.models import Max
from .models import *
import random
from copy import deepcopy
from .fetchAndStore import pullStoreFromAPI, storeDifficulty, storeFormat
import datetime
#first get 10 random question objects
#create a class with properties of that object
#yield a question, answer and options everytime it needs to be displayed

nums = 5
unique_sets = 20
#if unique_sets is changed, default of priority in Question model also needs to be changed

class Qns:
    questions=[]
    index=0
    correct=0
    isActive = False
    format=""

    @staticmethod
    def setQues(qns):
        Qns.questions=deepcopy(qns)

    @staticmethod
    def setQuiz(questions, format):
        pullStoreFromAPI()
        qs = questions
        Qns.setQues(qs)
        Qns.isActive = True
        Qns.format = format
        Stats.set_format(format)

    @staticmethod
    def resetQuiz():
        Qns.index = 0
        Qns.correct = 0
        Qns.isActive = False
        Qns.questions = []
        Qns.format = ""

    @staticmethod
    def isQuizOver(questions, answered=None):
        #for ScoreView
        if len(Qns.questions) == 0 and Qns.format == "":return False

        if Qns.format == "endless":
            if answered is True :return False
            elif answered is False :return True
            elif answered is None: return not Qns.isActive

        if Qns.index >= len(questions):return True

        return False

    @staticmethod
    def update_question(question, answered):

        question.asked+=1
        if answered:question.answered+=1
        if question.priority<=0:question.priority = unique_sets
        else: question.priority-=1

        question.save()


class Stats:
    date = datetime.date.today()
    all_difficulties = {}
    ans_difficulties = {}
    all_categories = {}
    ans_categories = {}
    all_time = {}
    ans_time = {}
    overall_difficulty = "random"
    format = ""

    @staticmethod
    def set_format(format):
        Stats.format = format
    @staticmethod
    def update_stats(question, answered, time):
        Stats.all_difficulties[question.difficulty.level] = Stats.all_difficulties.get(question.difficulty.level, 0) + 1
        Stats.all_categories[question.category.category] = Stats.all_categories.get(question.category.category, 0) + 1
        Stats.all_time[question.difficulty.level] = Stats.all_time.get(question.difficulty.level, 0) + time

        if answered:
            Stats.ans_difficulties[question.difficulty.level] = Stats.ans_difficulties.get(question.difficulty.level, 0) + 1
            Stats.ans_categories[question.category.category] = Stats.ans_categories.get(question.category.category, 0) + 1
            Stats.ans_time[question.difficulty.level] = Stats.ans_time.get(question.difficulty.level, 0) + time
        else:
            if Stats.format == "aggregate":
                Stats.ans_difficulties[question.difficulty.level] = Stats.ans_difficulties.get(
                    question.difficulty.level, 0) - 1
            else:
                Stats.ans_difficulties[question.difficulty.level] = Stats.ans_difficulties.get(question.difficulty.level, 0)
            Stats.ans_categories[question.category.category] = Stats.ans_categories.get(question.category.category, 0)
            Stats.ans_time[question.difficulty.level] = Stats.ans_time.get(question.difficulty.level, 0)
    @staticmethod
    def clear_stats():
        Stats.all_difficulties = {}
        Stats.ans_difficulties = {}
        Stats.all_categories = {}
        Stats.ans_categories = {}
        Stats.all_time = {}
        Stats.ans_time = {}
        Stats.format = ""

    @staticmethod
    def store_stats(user):
        difficulty = storeDifficulty(Stats.overall_difficulty, True)
        format = storeFormat(Stats.format, True)
        l_cat = min(Stats.ans_categories, key=Stats.ans_categories.get)
        m_cat = max(Stats.ans_categories, key=Stats.ans_categories.get)
        least_category = Categories.objects.get(category=l_cat)
        most_category = Categories.objects.get(category=m_cat)

        for level in ('easy', 'medium', 'hard'):
            if level not in Stats.all_difficulties.keys():
                Stats.all_difficulties[level] = 0
                Stats.all_time[level] = 0

                Stats.ans_difficulties[level] = 0
                Stats.ans_time[level] = 0
            elif level not in Stats.ans_difficulties.keys():
                Stats.ans_difficulties[level] = 0
                Stats.ans_time[level] = 0

        t = Tests(
            date = Stats.date,
            easy_count=Stats.all_difficulties['easy'],
            easy_answered=Stats.ans_difficulties['easy'],
            medium_count=Stats.all_difficulties['medium'],
            medium_answered=Stats.ans_difficulties['medium'],
            hard_count=Stats.all_difficulties['hard'],
            hard_answered=Stats.ans_difficulties['hard'],
            easy_total_time=Stats.all_time['easy'],
            medium_total_time=Stats.all_time['medium'],
            hard_total_time=Stats.all_time['hard'],
            easy_total_time_answered=Stats.ans_time['easy'],
            medium_total_time_answered=Stats.ans_time['medium'],
            hard_total_time_answered=Stats.ans_time['hard'],
            difficulty=difficulty,
            format=format,
            least_answered_category=least_category,
            most_answered_category=most_category,
            user=user
        )

        t.save()

def getMaxPriority():
    max = Questions.objects.aggregate(Max('priority'))['priority__max']

    if Questions.objects.all().filter(priority=max).count() < nums:
        if max <= 0:
            max = unique_sets
        else:
            max -= 1
        while Questions.objects.all().filter(priority=max).count() < nums:
            if max <= 0:
                max = unique_sets
            else:
                max -= 1

    return max
def standardQuestions(format=None):
    max = getMaxPriority()

    questions = list(Questions.objects.all().filter(priority=max))

    if format=="endless":
        questions = random.sample(questions, 100)
    else:
        questions = random.sample(questions, nums)

    return questions

def customQuestionsQuiz(id):
    title = CustomTitles.objects.all().filter(id=id)

    format = "custom"

    customs = list(Customs.objects.all().filter(title=title[0]))

    if len(customs) > nums:
        customs = random.sample(customs, nums)
    else:
        random.shuffle(customs)

    questions = []
    for question in customs:
        questions.append(question.question)

    return (questions, format)
def parseQuestion():
    for question in Qns.questions:

        qns = question.question
        a = question.answer
        c = question.category
        d = question.difficulty

        opts = Answers.objects.filter(question=question).values('answer')

        o=[]

        for opt in opts:
            o.append(opt['answer'])

        random.shuffle(o)

        yield {"q":qns, "a":a.answer, "c":c.category, "d":d.level, "o":o}