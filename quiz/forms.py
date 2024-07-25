import django.db.models
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.forms.utils import ErrorDict
from .models import Categories

#creating signup from
class SignupForm(UserCreationForm):
    class Meta:
        #declaring the model to save the form data in
        model=User

        #choosing the fields for the form
        fields=(
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['class'] = 'form-control text-center'
        self.fields['password1'].widget.attrs['class'] = 'form-control text-center'
        self.fields['password2'].widget.attrs['class'] = 'form-control text-center'
        self.fields['first_name'].widget.attrs['class'] = 'form-control text-center'
        self.fields['last_name'].widget.attrs['class'] = 'form-control text-center'
        self.fields['email'].widget.attrs['class'] = 'form-control text-center'

        self.fields['username'].widget.attrs['placeholder'] = 'Enter your username'
        self.fields['password1'].widget.attrs['placeholder'] = 'Enter your password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm your password'
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter your first name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter your last name'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter your email'



#creating login form
class LoginForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['class'] = 'form-control text-center'
        self.fields['password'].widget.attrs['class'] = 'form-control text-center'

        self.fields['username'].widget.attrs['placeholder'] = 'Enter your username'
        self.fields['password'].widget.attrs['placeholder'] = 'Enter your password'

    def confirm_login_allowed(self, user):
        pass


class CustomQuizForm(forms.Form):
    question = forms.CharField(label="Question")
    answer = forms.CharField(label = "Answer")
    opt1 = forms.CharField(label = "Option 1")
    opt2 = forms.CharField(label = "Option 2")
    opt3 = forms.CharField(label = "Option 3")

    cats = Categories.objects.all()

    CAT_CHOICES = [(cat.category, cat.category.replace("_"," ").title()) for cat in cats]
    CAT_CHOICES.append(("custom", "Create a new category"))
    CAT_CHOICES = tuple(CAT_CHOICES)

    DIFFICULTY_CHOICES = (
        ("easy", "Easy"),
        ("medium", "Medium"),
        ("hard", "Hard"),
    )

    difficulty = forms.ChoiceField(label="Difficulty", choices=DIFFICULTY_CHOICES)
    cat = forms.ChoiceField(label="Category", choices=CAT_CHOICES, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['question'].widget.attrs['class'] = 'form-control my-0 text-center'
        self.fields['answer'].widget.attrs['class'] = 'form-control my-0 text-center'
        self.fields['opt1'].widget.attrs['class'] = 'form-control my-0 text-center'
        self.fields['opt2'].widget.attrs['class'] = 'form-control my-0 text-center'
        self.fields['opt3'].widget.attrs['class'] = 'form-control my-0 text-center'
        self.fields['cat'].widget.attrs['class'] = 'form-control my-0 text-center'
        self.fields['difficulty'].widget.attrs['class'] = 'form-control my-0 text-center'

        self.fields['question'].widget.attrs['placeholder'] = 'Enter the question'
        self.fields['answer'].widget.attrs['placeholder'] = 'Enter the answer'
        self.fields['opt1'].widget.attrs['placeholder'] = 'Option 1'
        self.fields['opt2'].widget.attrs['placeholder'] = 'Option 2'
        self.fields['opt3'].widget.attrs['placeholder'] = 'Option 3'
        self.fields['cat'].widget.attrs['placeholder'] = 'Category'
        self.fields['difficulty'].widget.attrs['placeholder'] = 'Difficulty'


class CustomQuizTitle(forms.Form):
    title = forms.CharField(label="Quiz title")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['title'].widget.attrs['class'] = 'form-control my-0 text-center'
        self.fields['title'].widget.attrs['placeholder'] = 'Enter the quiz title'
