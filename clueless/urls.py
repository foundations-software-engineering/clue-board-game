"""clueless URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from clueless import views
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^lobby/', views.lobby, name='lobby'),
    url(r'^login/', views.login, name='login'),
    url(r'^logout/', views.logout, name='logout'),
    url(r'^play/(?P<game_id>\d+)/', views.playgame, name='playgame'),
    url(r'^startgame/', views.startgame, name='startgame'),
    url(r'^playerturn/',TemplateView.as_view(template_name="clueless/playerturn.html"),name='playerturn'),
    url(r'^joingame/(?P<game_id>\d+)/', views.joingame, name='joingame'),
    url(r'^begingame/(?P<game_id>\d+)/', views.begingame, name='begingame'),
    url(r'^controllers/startgame/', views.start_game_controller, name='start_game_controller'),
    url(r'^controllers/joingame/', views.join_game_controller, name='join_game_controller'),
    url(r'^controllers/begingame/', views.begin_game_controller, name='begin_game_controller'),
    url(r'^$', views.index, name='index'),
]
