# Generated by Django 3.0.8 on 2020-09-23 16:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gigs', '0029_requirementclient_delivered'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='requirementclient',
            name='userFile',
        ),
        migrations.AddField(
            model_name='requirementclient',
            name='files',
            field=models.ManyToManyField(to='gigs.UserFile'),
        ),
    ]
