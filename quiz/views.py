from django.shortcuts import render, reverse, redirect
from django.http import HttpResponse, JsonResponse
from django.views import View
from .fetchAndStore import pullStoreFromAPI, getAPI
from .forms import SignupForm, LoginForm, CustomQuizForm, CustomQuizTitle
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from .quizLogic import standardQuestions, parseQuestion, Qns, customQuestionsQuiz, Stats
from .crud import storeTitle, storeCustomQuestionAnswer, getCustomTitles, getYourQuestions, getAllCustoms, getRecord, getBest
from .models import *
from .utils import *
import uuid
# Create your views here.

class Index(View):

    def get(self, req):
        if req.user.is_authenticated:
            if not Profile.objects.filter(user = req.user)[0].is_verfied:
                return redirect('quiz:verify')

        if Qns.isActive is False:
            return render(req, 'index.html')
        else:
            return redirect('quiz:quiz')
#needs login, so LoginRequiredMixin

class SignUpView(View):
    def get(self, req):
        if Qns.isActive is False:
            if req.user.is_authenticated:
                if not Profile.objects.filter(user=req.user)[0].is_verfied:
                    return redirect('quiz:verify')

            #if get, simply render the form
            form=SignupForm
            ctx={"form":form}
            return render(req, 'signup.html', ctx)
        else:
            return redirect('quiz:quiz')

    def post(self, req):

        #if post, validate and save
        form=SignupForm(req.POST)

        errors=None


        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            if User.objects.all().filter(email = email).count() > 0:
                errors = {"used_email" : "This email is already used by another account"}
            else:
                form.save()
                user_obj = User.objects.all().filter(username = username)[0]
                p = Profile(user = user_obj, email_token=str(uuid.uuid4()))
                p.save()
                return redirect('quiz:login')
        else:
            errors=form.errors

        ctx={"form":form, "errors":errors}

        return render(req, 'signup.html', ctx)


class LogInView(View):

    #if get, simply render the form
    def get(self, req):

        if Qns.isActive is False:

            next = req.GET.get('next', None)
            if next is not None:
                next = next[1:len(next)-1]

            if req.user.is_authenticated:return redirect('quiz:index')

            form=LoginForm
            ctx={"form":form, "next":next}
            return render(req,'login.html',ctx)
        else:
            return redirect('quiz:quiz')

    def post(self, req):
        form=LoginForm(data=req.POST)

        errors = None

        #validate
        if form.is_valid():
            user=authenticate(req, username=form.cleaned_data['username'], password=form.cleaned_data['password'])

            #if authenticated, then log in the user and redirect
            if user is not None:
                login(req, user)

                if "next" in req.POST.keys():
                    next = req.POST['next']
                    return redirect('quiz:'+next)
                return redirect('quiz:index')
        else:
            errors=form.errors

        ctx={"form":form, "errors":errors}

        #if not valid/authenticated, display form again
        return render(req, 'login.html', ctx)

class LogOutView(LoginRequiredMixin, View):

    login_url = "quiz:login"

    def get(self, req):
        if Qns.isActive is False:
            Qns.resetQuiz()
            Stats.clear_stats()
            logout(req)
            return redirect('quiz:index')
        else:
            return redirect('quiz:quiz')

class VerifyView(LoginRequiredMixin, View):

    login_url = "quiz:login"

    def get(self, req, token=None):
        if Profile.objects.get(user = req.user).is_verfied:
            return redirect('quiz:index')


        p = Profile.objects.get(user = req.user)

        if token is None:

            send_email_token(req.user.email, p.email_token)
            return render(req, 'verify.html', {"token":False})
        else:

            if token==p.email_token:

                p.is_verfied = True
                p.save()
                return redirect('quiz:index')
            else:
                print("6")

                send_email_token(req.user.email, p.email_token)
                return render(req, 'verify.html', {"token":True, "correct":False})

class QuizView(LoginRequiredMixin,View):

    login_url = "quiz:login"

    #to render the quiz
    def get(self, req):

        if req.user.is_authenticated:
            if not Profile.objects.filter(user=req.user)[0].is_verfied:
                return redirect('quiz:verify')

        if not Qns.isActive:return redirect('quiz:index')

        #get questions
        questions = list(parseQuestion())

        if Qns.isQuizOver(questions):

            if Stats.format != "":
                #if quiz over, then finalize score and return score screen
                Stats.store_stats(req.user)
                Stats.clear_stats()
                Qns.isActive = False

            return redirect('quiz:score')
        else:

            #if quiz not over, send the question to the quiz screen
            question = questions[Qns.index]
            ctx={"q": question['q'], "a":question['a'], "c": question['c'], "d":question['d'], "opts":question['o'], "score": Qns.correct, "format":Qns.format}

        return render(req, 'quiz.html', ctx)

    #to receive the answer of previous question and send new question
    def post(self, req):

        if 'isQuit' in req.POST.keys():
            Qns.resetQuiz()
            Stats.clear_stats()
            return redirect('quiz:index')
        else:
            Qns.index += 1

            questions = list(parseQuestion())

            #checks answer to update score
            answered = None
            if not Qns.index>len(questions):
                if req.POST['answer'] == Qns.questions[Qns.index - 1].answer.answer:
                    Qns.correct += 1
                    answered = True
                else:
                    answered = False
                    if Qns.format == "aggregate": Qns.correct-=1

                Qns.update_question(Qns.questions[Qns.index - 1], answered)

                Stats.update_stats(Qns.questions[Qns.index - 1], answered, round((float(req.POST['time'])/1000),5))

            if Qns.isQuizOver(questions, answered=answered):
                #if fetch not stopped, then signal it to stop
                if "over" not in req.POST.keys():
                    ctx = {"over":"over"}
                else:
                    #if fetch stopped, finalize scores and go to score screen

                    Stats.store_stats(req.user)
                    Stats.clear_stats()
                    Qns.isActive = False

                    return redirect('quiz:score')
            else:
                #if quiz not over, send a new question
                question = questions[Qns.index]
                ctx = {"q": question['q'], "a": question['a'], "c": question['c'], "d": question['d'],
                       "opts": question['o'], "score": Qns.correct, "format":Qns.format}

            #response for fetch API
            return JsonResponse(ctx)


class StandardQuizView(LoginRequiredMixin, View):
    login_url = "quiz:login"

    def get(self, req):
        if req.user.is_authenticated:
            if not Profile.objects.filter(user=req.user)[0].is_verfied:
                return redirect('quiz:verify')

        if not Qns.isActive:
            Qns.setQuiz(standardQuestions(), "standard")

        return redirect('quiz:quiz')

class TimedQuizView(LoginRequiredMixin, View):
    login_url = "quiz:login"

    def get(self, req):
        if req.user.is_authenticated:
            if not Profile.objects.filter(user=req.user)[0].is_verfied:
                return redirect('quiz:verify')

        if not Qns.isActive:
            Qns.setQuiz(standardQuestions(), "timed")

        return redirect('quiz:quiz')


class EndlessQuizView(LoginRequiredMixin, View):
    login_url = "quiz:login"

    def get(self, req):
        if req.user.is_authenticated:
            if not Profile.objects.filter(user=req.user)[0].is_verfied:
                return redirect('quiz:verify')

        if not Qns.isActive:
            Qns.setQuiz(standardQuestions("endless"), "endless")

        return redirect('quiz:quiz')


class AggregateQuizView(LoginRequiredMixin, View):
    login_url = "quiz:login"

    def get(self, req):
        if req.user.is_authenticated:
            if not Profile.objects.filter(user=req.user)[0].is_verfied:
                return redirect('quiz:verify')

        if not Qns.isActive:
            Qns.setQuiz(standardQuestions("aggregate"), "aggregate")

        return redirect('quiz:quiz')

class CustomQuizCreate(LoginRequiredMixin, View):

    login_url = "quiz:login"

    def get(self, req):
        if req.user.is_authenticated:
            if not Profile.objects.filter(user=req.user)[0].is_verfied:
                return redirect('quiz:verify')

        if Qns.isActive is False:

            form = CustomQuizTitle

            ctx = {"form":form}

            return render(req, 'create.html', ctx)
        else:
            return redirect('quiz:quiz')

    def post(self, req):

        if "title" in req.POST.keys():
            inForm = CustomQuizTitle(req.POST)
            isTitleForm = True
        else:
            inForm = CustomQuizForm(req.POST)
            isTitleForm = False

        errors = None
        duplicates = None

        if inForm.is_valid() or "falseValid" in req.POST.keys():
            if isTitleForm:
                title = inForm.cleaned_data['title'].replace(' ', '_').lower()
                title = storeTitle(title, req.user)

                if title is None:
                    renderForm=inForm
                    duplicates = ["quiz title"]
                else:
                    renderForm = CustomQuizForm
                    title = title.title

                ctx = {"form": renderForm, "duplicates": duplicates, "errors": errors, "passed_title":title}
                return render(req, 'create.html', ctx)
            else:
                title = req.POST['passed_title']
                renderForm = CustomQuizForm

                if not "falseValid" in req.POST.keys():
                    question = inForm.cleaned_data['question']
                    answer = inForm.cleaned_data['answer']
                    opt1 = inForm.cleaned_data['opt1']
                    opt2 = inForm.cleaned_data['opt2']
                    opt3 = inForm.cleaned_data['opt3']
                    difficulty = inForm.cleaned_data['difficulty']
                    category = inForm.cleaned_data['cat']
                    if category == "custom":
                        category = req.POST['hidden'].lower().replace(" ", "_")


                    (isNewQuestion, isNewCustom) = storeCustomQuestionAnswer(difficulty, category, (opt1, opt2, opt3,), answer, question, title)

                    if not isNewCustom or not isNewQuestion:
                        duplicates = []

                        if not isNewQuestion: duplicates.append("question")
                        if not isNewCustom: duplicates.append("custom")
                        renderForm = inForm


        else:
            errors = inForm.errors
            title = req.POST['passed_title']

            renderForm=inForm

        ctx = {"form":renderForm, "duplicates":duplicates, "errors":errors, "passed_title":title}
        return render(req, 'create.html', ctx)


class YourCustomView(LoginRequiredMixin, View):

    login_url = "quiz:login"

    def get(self, req):

        if req.user.is_authenticated:
            if not Profile.objects.filter(user=req.user)[0].is_verfied:
                return redirect('quiz:verify')

        if Qns.isActive is False:

            (quizzes, empty) = getCustomTitles(req.user)

            ctx={"empty":empty, "quizzes":quizzes}

            response = render(req, 'manage.html', ctx)
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'

            return response
        else:
            return redirect("quiz:quiz")

    def post(self, req):
        if 'isDelete' in req.POST.keys():
            CustomTitles.objects.filter(title=req.POST['isDelete']).delete()
            pass

        if 'oldTitle' in req.POST.keys() and 'newTitle' in req.POST.keys():
            t = CustomTitles.objects.get(title=req.POST['oldTitle'])
            t.title = req.POST['newTitle'].strip().replace(' ', '_').lower()
            t.save()

        return JsonResponse({})

class YourQuestionView(LoginRequiredMixin, View):

    login_url = "quiz:login"

    def get(self, req, title=None):

        if req.user.is_authenticated:
            if not Profile.objects.filter(user=req.user)[0].is_verfied:
                return redirect('quiz:verify')

        if Qns.isActive is False:

            (quests, empty) = getYourQuestions(req.user, title)

            if quests is None:
                return redirect('quiz:manage')

            questions=[]

            for question in quests:
                opt_obj = Answers.objects.all().filter(question=question.question)
                opts = (opt.answer for opt in opt_obj if not opt.answer == question.question.answer.answer)
                questions.append((question,list(opts)))


            ctx = {"empty":empty, "questions":questions, "title":title}
            response = render(req, 'edit.html', ctx)
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            return response
        else:
            return redirect('quiz:quiz')

    def post(self, req, title):
        if 'isDelete' in req.POST.keys():
            Customs.objects.filter(id=req.POST['isDelete']).delete()

        return JsonResponse({})

class AllCustoms(LoginRequiredMixin, View):

    login_url = "quiz:login"

    def get(self,req):
        if req.user.is_authenticated:
            if not Profile.objects.filter(user=req.user)[0].is_verfied:
                return redirect('quiz:verify')

        if Qns.isActive is False:
            (quizzes,empty)=getAllCustoms()

            return render(req, 'customs.html', {"quizzes":quizzes, "empty":empty})
        else:
            return redirect('quiz:quiz')

    def post(self, req):
        if not Qns.isActive:
            customs = customQuestionsQuiz(int(req.POST['titleId']))
            Qns.setQuiz(customs[0], customs[1])


        return redirect('quiz:quiz')


class TrackRecord(LoginRequiredMixin, View):

    login_url = "quiz:login"

    def get(self, req):
        if req.user.is_authenticated:
            if not Profile.objects.filter(user=req.user)[0].is_verfied:
                return redirect('quiz:verify')

        if Qns.isActive is False:
            (records,best,worst) = getRecord(req.user)
            if records is None:
                empty= True
            else:
                empty = False
            return render(req, 'record.html', {"records":records, "empty":empty, "best":best, "worst":worst})
        else:
            return redirect('quiz:quiz')

class ScoreView(LoginRequiredMixin, View):

    login_url = 'quiz:login'

    def get(self, req):
        if req.user.is_authenticated:
            if not Profile.objects.filter(user=req.user)[0].is_verfied:
                return redirect('quiz:verify')

        if Qns.isActive:
            return redirect('quiz:quiz')
        elif not Qns.isQuizOver(Qns.questions):
            Qns.resetQuiz()
            return redirect('quiz:record')
        else:
            if len(Qns.questions)!=0:
                if Qns.format!="endless" and Qns.format != "aggregate":
                    score = round(float(Qns.correct)/len(Qns.questions) * 100, 4)
                    score = str(score)+"%"
                else:
                    score = Qns.correct
            else:
                score = "0.0%"

            (personal, overall) = getBest(req.user, Qns.format)

            Qns.resetQuiz()

            if personal is None:
                personal_best = None
            else:
                personal_best = personal['score']

            if overall is None:
                overall_best = None
                format = None
            else:
                overall_best = (overall['test'].user.get_full_name(), overall['score'])
                format = overall['test'].format.format

            return render(req, "score.html", {"score":score, "personal_best":personal_best, "overall_best":overall_best, "format":format})