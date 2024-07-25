# Generated by Django 4.2 on 2023-06-22 21:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0004_alter_tests_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questions',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz.categories'),
        ),
        migrations.AlterField(
            model_name='questions',
            name='difficulty',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz.difficulties'),
        ),
        migrations.AlterField(
            model_name='tests',
            name='difficulty',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz.difficulties'),
        ),
        migrations.AlterField(
            model_name='tests',
            name='format',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz.formats'),
        ),
        migrations.AlterField(
            model_name='tests',
            name='least_answered_category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='least_answered', to='quiz.categories'),
        ),
        migrations.AlterField(
            model_name='tests',
            name='most_answered_category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='most_answered', to='quiz.categories'),
        ),
    ]
