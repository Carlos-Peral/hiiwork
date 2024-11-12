# Generated by Django 3.0.5 on 2020-05-05 09:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gigs', '0006_auto_20200505_0332'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='feature',
            name='category',
        ),
        migrations.RemoveField(
            model_name='feature',
            name='created',
        ),
        migrations.AddField(
            model_name='feature',
            name='gig',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='gigs.Gig'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='feature',
            name='tier1',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='feature',
            name='tier2',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='feature',
            name='tier3',
            field=models.BooleanField(default=False),
        ),
    ]