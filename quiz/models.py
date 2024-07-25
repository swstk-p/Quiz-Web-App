from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

# Create your models here.

#this is the table for difficulty level
class Difficulties(models.Model):
    level=models.TextField(blank=False, null=False, unique=True)

#this is the table for all categories
class Categories(models.Model):
    category=models.TextField(unique=True, blank=False, null=False)

#this is the table for quiz formats
class Formats(models.Model):
    format=models.TextField(unique=True, blank=False, null=False)

#this is the table for profile (mainly to see if verified or not)
class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, unique=True)
    email_token = models.CharField(max_length=200)
    is_verfied = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'email_token'],
                name="same user cannot have multiple email tokens"
            )
        ]


#this is the table for all the answers and options
class Answers(models.Model):
    answer=models.TextField()
    question=models.ForeignKey("Questions", on_delete=models.CASCADE, null=True, blank=False)

#this is the table to store the questions
class Questions(models.Model):
    question=models.TextField(blank=False, null=False, unique=True)
    answer=models.OneToOneField(Answers, on_delete=models.CASCADE, null=False, blank=False)
    difficulty=models.ForeignKey(Difficulties, on_delete=models.CASCADE, null=False, blank=False)
    category=models.ForeignKey(Categories, on_delete=models.CASCADE, null=False, blank=False)
    priority=models.IntegerField(null=False, blank=False, default=15)
    asked=models.IntegerField(null=False, blank=False, default=0)
    answered=models.IntegerField(null=False, blank=False, default=0)

#this is the table to store the customsets

class CustomTitles(models.Model):
    title = models.TextField(blank=False, null=False)
    host = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)

    class Meta:
        constraints=[
            models.UniqueConstraint(
                fields=['title','host'],
                name="each_host_has_unique_title"
            )
        ]

#this is the table to idenfity the default questions
class Customs(models.Model):
    question=models.ForeignKey(Questions, on_delete=models.CASCADE, null=False, blank=False)
    title=models.ForeignKey(CustomTitles, on_delete=models.CASCADE, null=False, blank=False)

    class Meta:
        constraints=[
            models.UniqueConstraint(
                fields=['question','title'],
                name="each_title_has_unique_questions"
            )
        ]

#this is the table to store information about tests
class Tests(models.Model):
    user=models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)
    date=models.DateField(null=False, blank=False)
    format=models.ForeignKey(Formats, blank=False, null=False, on_delete=models.CASCADE)
    difficulty=models.ForeignKey(Difficulties, blank=False, null=False, on_delete=models.CASCADE)
    easy_count=models.IntegerField(null=False, blank=False)
    easy_answered=models.IntegerField(null=False, blank=False)
    medium_count=models.IntegerField(null=False, blank=False)
    medium_answered=models.IntegerField(null=False, blank=False)
    hard_count=models.IntegerField(null=False, blank=False)
    hard_answered=models.IntegerField(null=False, blank=False)
    easy_total_time=models.FloatField(null=False, blank=False)
    medium_total_time=models.FloatField(null=False, blank=False)
    hard_total_time=models.FloatField(null=False, blank=False)
    easy_total_time_answered=models.FloatField(null=False, blank=False)
    medium_total_time_answered=models.FloatField(null=False, blank=False)
    hard_total_time_answered=models.FloatField(null=False, blank=False)
    most_answered_category=models.ForeignKey(Categories, related_name='most_answered', blank=False, null=False, on_delete=models.CASCADE)
    least_answered_category=models.ForeignKey(Categories, related_name='least_answered', blank=False, null=False, on_delete=models.CASCADE)