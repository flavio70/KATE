from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^gitlab_webhook/$', views.gitlab_webhook, name='gitlab_webhook'),
]
