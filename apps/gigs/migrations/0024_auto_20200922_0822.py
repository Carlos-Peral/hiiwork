# Generated by Django 3.0.8 on 2020-09-22 13:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gigs', '0023_auto_20200922_0754'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='review',
            name='order',
        ),
        migrations.AddField(
            model_name='userfile',
            name='url_modifier',
            field=models.TextField(default='gig-media', max_length=255),
            preserve_default=False,
        ),
    ]
