from django.urls import path

from . import views

app_name = "quiz"

urlpatterns = [
    path('', views.Index.as_view(), name="index"),
    path('signup/', views.SignUpView.as_view(), name="signup"),
    path('login/', views.LogInView.as_view(), name="login"),
    path('logout/', views.LogOutView.as_view(), name="logout"),
    path('quiz/', views.QuizView.as_view(), name='quiz'),
    path('standard/', views.StandardQuizView.as_view(), name='standard'),
    path('timed/', views.TimedQuizView.as_view(), name='timed'),
    path('manage/', views.YourCustomView.as_view(), name='manage'),
    path('create/', views.CustomQuizCreate.as_view(), name='create'),
    path('edit/', views.YourQuestionView.as_view(), name='edit'),
    path('edit/<slug:title>/', views.YourQuestionView.as_view(), name='edit'),
    path('customs/', views.AllCustoms.as_view(), name='customs'),
    path('record/', views.TrackRecord.as_view(), name='record'),
    path('endless/', views.EndlessQuizView.as_view(), name='endless'),
    path('aggregate/', views.AggregateQuizView.as_view(), name='aggregate'),
    path('score/', views.ScoreView.as_view(), name="score"),
    path('verify/', views.VerifyView.as_view(), name="verify"),
    path('verify/<slug:token>/', views.VerifyView.as_view(), name="verify"),
    #check loginrequiredmixin
]