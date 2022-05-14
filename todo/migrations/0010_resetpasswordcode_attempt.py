# Generated by Django 3.2 on 2022-05-13 11:34

from django.db import migrations, models
import todo.validators


class Migration(migrations.Migration):

    dependencies = [
        ('todo', '0009_remove_task_overdue'),
    ]

    operations = [
        migrations.AddField(
            model_name='resetpasswordcode',
            name='attempt',
            field=models.SmallIntegerField(blank=True, default=5, validators=[todo.validators.validate_attempt]),
        ),
    ]