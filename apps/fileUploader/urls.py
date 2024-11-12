from django.urls import path, include
from apps.fileUploader import views

urlpatterns = [
    path('upload/',
         views.uploadFile, name='upload-file'),
    path('delete/',
         views.deleteFile, name='delete-file'),

]
