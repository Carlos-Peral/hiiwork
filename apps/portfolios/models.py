from django.db import models
from django.conf import settings
from apps.gigs.models import UserImage
from talentSite.storage_backends import StaticStorage
from apps.portfolios.choices import *
from datetime import datetime

User = settings.AUTH_USER_MODEL


class Ability(models.Model):
    name = models.CharField(max_length=30, unique=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Program(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def generate_filename(self, filename):
        url = "%/programImages/%s" % (str(self.id), filename)
        return url
    logo = models.ImageField(
        storage=StaticStorage(file_overwrite=False), upload_to=generate_filename, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class LanguageName(models.Model):
    name = models.CharField(max_length=15, unique=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class LanguageLevel(models.Model):
    level = models.CharField(max_length=2, choices=LEVEL_CHOICES, unique=True)

    def __str__(self):
        return self.level

    def __unicode__(self):
        return self.level


class Language(models.Model):
    name = models.ForeignKey(LanguageName, on_delete=models.CASCADE)
    level = models.ForeignKey(LanguageLevel, on_delete=models.CASCADE)

    def __str__(self):
        return self.name + self.level

    def __unicode__(self):
        return self.name + self.level


class Portfolio(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    about = models.TextField(max_length=600, null=True)
    abilities = models.ManyToManyField(Ability, blank=True)
    programs = models.ManyToManyField(Program, blank=True)
    languages = models.ManyToManyField(Language, blank=True)
    experience = models.TextField()
    education = models.TextField(blank=True)
    gallery = models.ManyToManyField(
        UserImage, related_name='%(app_label)s_%(class)s_gallery')

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username + '\'s portfolio'

    def __unicode__(self):
        return self.user.username + '\'s portfolio'
