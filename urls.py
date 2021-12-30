from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index,name='home'),
    path('extract/', views.extract, name='extract'),
    path('writepage/', views.writepage, name='writepage'),
    # path('camera', views.camera, name='camera'),
    path('upload', views.upload, name='upload'),
    path('blink', views.command, name='blinkcmmd')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)