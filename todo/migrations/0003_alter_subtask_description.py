# Generated by Django 4.0.4 on 2022-04-19 08:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todo', '0002_task_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subtask',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]