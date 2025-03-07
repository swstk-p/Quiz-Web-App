# Generated by Django 4.2 on 2023-06-22 16:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('quiz', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_token', models.CharField(max_length=200)),
                ('is_verfied', models.BooleanField(default=False)),
            ],
        ),
        migrations.RemoveField(
            model_name='sessions',
            name='host',
        ),
        migrations.RemoveConstraint(
            model_name='tests',
            name='unique_user_session_combination',
        ),
        migrations.RemoveField(
            model_name='tests',
            name='session',
        ),
        migrations.AddConstraint(
            model_name='customs',
            constraint=models.UniqueConstraint(fields=('question', 'title'), name='each_title_has_unique_questions'),
        ),
        migrations.DeleteModel(
            name='Sessions',
        ),
        migrations.AddField(
            model_name='profile',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddConstraint(
            model_name='profile',
            constraint=models.UniqueConstraint(fields=('user', 'email_token'), name='same user cannot have multiple email tokens'),
        ),
    ]
