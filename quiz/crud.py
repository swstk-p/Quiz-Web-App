from .models import *
from .fetchAndStore import storeCategory, storeDifficulty, storeFormat
from django.db import IntegrityError
from django.db.models import Max



def storeTitle(title, user):
    if len(CustomTitles.objects.filter(title=title, host=user).values()) < 1:
        custom_title = CustomTitles(title=title, host=user)
        custom_title.save()
    else:
        custom_title = None

    return custom_title

def storeCustomQuestionAnswer(difficulty, category, options, answer, question, title):

    #saving difficulty
    diff = storeDifficulty(difficulty, True)

    #saving category
    cat = storeCategory(category, True)

    # saving options
    for opt in options:
        o = Answers(answer=opt, question=None)
        o.save()

    # saving the answer
    a = Answers(answer=answer, question=None)
    a.save()

    q_saved = False

    # saving the question
    try:
        q = Questions(question=question, answer=a, difficulty=diff, category=cat, priority=20, asked=0, answered=0)
        q.save()
        q_saved = True
    except IntegrityError as e:
        Answers.objects.filter(question=None).delete()

    if q_saved:
        Answers.objects.filter(question=None).update(question=q)

    # obtaining question
    qns = Questions.objects.get(question=question)

    try:
        t = CustomTitles.objects.get(title=title)
        c = Customs(question=qns, title=t)
        c.save()
        c_saved = True
    except IntegrityError as e:
        c_saved = False

    return (q_saved, c_saved)

def getCustomTitles(user):
    titles = CustomTitles.objects.all().filter(host=user)

    quizzes = []
    for title in titles:
        quizzes.append((title, Customs.objects.filter(title=title).count()))

    if len(titles) < 1:
        empty = True
    else:
        empty = False

    return (quizzes, empty)

def getYourQuestions(user, title):

    if title is None:
        return(None, True)

    ttl = CustomTitles.objects.all().filter(title=title, host=user)

    if len(ttl)<1:
        return(None, True)
    else:
        questions = Customs.objects.all().filter(title=ttl[0])
        # questions=[]

        # for question in quiz:
        #     questions.append((title, Customs.objects.filter(title=title).count()))

        if len(questions) < 1:
            empty = True
        else:
            empty = False

        return (questions, empty)

def getAllCustoms():
    titles = CustomTitles.objects.all()

    quizzes = []
    for title in titles:
        if not Customs.objects.filter(title=title).count() < 1:
            quizzes.append((title, Customs.objects.filter(title=title).count()))

    if len(titles) < 1:
        empty = True
    else:
        empty = False

    return (quizzes, empty)

def getRecord(user):
    tests = Tests.objects.all().filter(user = user).order_by('-id')
    if len(tests)<1:
        return (None, None, None)

    records=[]
    best = {}
    worst= {}

    for test in tests:
        record = {}
        if test.format.format == "endless" or test.format.format == "aggregate":
            score = test.easy_answered + test.medium_answered + test.hard_answered
        else:
            score = round(float(test.easy_answered + test.medium_answered + test.hard_answered)/(test.easy_count + test.medium_count + test.hard_count) * 100,4)

        if test.format.format!="endless" and test.format.format!="aggregate":
            if len(best) < 1 or best["score"] <= score:
                best['test'] = test
                best['score'] = score
            if len(worst) < 1 or worst['score'] > score:
                worst['test'] = test
                worst['score'] = score

        ans = {}
        total_time = {}
        correct_time = {}
        td = {}

        if not test.easy_count == 0:
            if not test.format.format == "aggregate":
                ans['easy'] = round(float(test.easy_answered)/test.easy_count * 100, 4)
            else:
                ans['easy'] = test.easy_answered
            total_time['easy'] = test.easy_total_time / test.easy_count

            if not test.easy_answered == 0:
                correct_time['easy'] = test.easy_total_time_answered / test.easy_answered
            else:
                correct_time['easy'] = "N/A"

            if correct_time['easy'] == "N/A":
                td['easy'] = "N/A"
            else:
                difference = round(correct_time['easy'] - total_time['easy'],3)
                if difference < 0:
                    difference = abs(difference)
                    td['easy'] = f"{difference}s faster"
                else:
                    td['easy'] = f"{difference}s slower"

        else:
            ans['easy'] = "N/A"
            total_time['easy'] = "N/A"
            correct_time['easy'] = "N/A"
            td['easy'] = "N/A"

        if not test.medium_count == 0:
            if not test.format.format == "aggregate":
                ans['medium'] = round(float(test.medium_answered)/test.medium_count * 100, 4)
            else:
                ans['medium'] = test.medium_answered

            total_time['medium'] = test.medium_total_time / test.medium_count

            if not test.medium_answered == 0:
                correct_time['medium'] = test.medium_total_time_answered / test.medium_answered
            else:
                correct_time['medium'] = "N/A"

            if correct_time['medium'] == "N/A":
                td['medium'] = "N/A"
            else:
                difference = round(correct_time['medium'] - total_time['medium'],3)
                if difference < 0:
                    difference = abs(difference)
                    td['medium'] = f"{difference}s faster"
                else:
                    td['medium'] = f"{difference}s slower"

        else:
            ans['medium'] = "N/A"
            total_time['medium'] = "N/A"
            correct_time['medium'] = "N/A"
            td['medium'] = "N/A"

        if not test.hard_count == 0:
            if not test.format.format == "aggregate":
                ans['hard'] = round(float(test.hard_answered)/test.hard_count * 100, 4)
            else:
                ans['hard'] = test.hard_answered

            total_time['hard'] = test.hard_total_time / test.hard_count

            if not test.hard_answered == 0:
                correct_time['hard'] = test.hard_total_time_answered / test.hard_answered
            else:
                correct_time['hard'] = "N/A"

            if correct_time['hard'] == "N/A":
                td['hard'] = "N/A"
            else:
                difference = round(correct_time['hard'] - total_time['hard'],3)
                if difference < 0:
                    difference = abs(difference)
                    td['hard'] = f"{difference}s faster"
                else:
                    td['hard'] = f"{difference}s slower"

        else:
            ans['hard'] = "N/A"
            total_time['hard'] = "N/A"
            correct_time['hard'] = "N/A"
            td['hard'] = "N/A"

        record["test"] = test
        record["score"] = score
        record["answered"] = ans
        record["td"] = td
        record['lac'] = test.least_answered_category.category.replace('_', " ").title().split()[0]
        record['mac'] = test.most_answered_category.category.replace('_', " ").title().split()[0]

        if td['easy'] == td['medium'] == td['hard'] == 'N/A':
            record['lac'] = record['mac'] = 'N/A'

        records.append(record)

    return (records, best['test'], worst['test'])

def getBest(user, f):

    personal_best = {}
    overall_best = {}

    format = storeFormat(f, True)

    tests = Tests.objects.all().filter(user=user, format=format).order_by('-id')
    if len(tests) < 1:
        personal_best = None
    else:
        for test in tests:
            if test.format.format == "endless" or test.format.format == "aggregate":
                score = test.easy_answered + test.medium_answered + test.hard_answered
            else:
                score = round(float(test.easy_answered + test.medium_answered + test.hard_answered) / (
                            test.easy_count + test.medium_count + test.hard_count) * 100, 4)

            if len(personal_best) < 1 or personal_best["score"] <= score:
                personal_best['test'] = test
                personal_best['score'] = score

    overall_tests = Tests.objects.all().filter(format=format).order_by('-id')
    if len(overall_tests) < 1:
        overall_best = None
    else:
        for test in overall_tests:
            if test.format.format == "endless" or test.format.format == "aggregate":
                score = test.easy_answered + test.medium_answered + test.hard_answered
            else:
                score = round(float(test.easy_answered + test.medium_answered + test.hard_answered) / (
                        test.easy_count + test.medium_count + test.hard_count) * 100, 4)

            if len(overall_best) < 1 or overall_best["score"] <= score:
                overall_best['test'] = test
                overall_best['score'] = score

    return (personal_best, overall_best)
