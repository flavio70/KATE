from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^login/$', views.login, name='login'),
	url(r'^logout/$', views.logout, name='logout'),
	url(r'^check_login/$', views.check_login, name='check_login'),
	url(r'^development_index/$', views.development_index, name='development_index'),
	url(r'^suite_creator/$', views.suite_creator, name='suite_creator'),
	url(r'^test_development/$', views.test_development, name='test_development'),
	url(r'^accesso/$', views.accesso, name="accesso"),
	url(r'^tuning/$', views.tuning, name="tuning"),
	url(r'^selectEqpt/$', views.selectEqpt),
	url(r'^tuningEngine/$', views.tuningEngine),
	url(r'^runJenkins/$', views.runJenkins),
	url(r'^viewJobDetails/$', views.viewJobDetails),
	url(r'^viewBuildDetails/$', views.viewBuildDetails),
	url(r'^createRunJenkins/$', views.createRunJenkins),
	url(r'^createNewTest/$', views.createNewTest),
	url(r'^viewReport/$', views.viewReport),
	url(r'^collectReports/$', views.collectReports),
	url(r'^add_bench/$', views.add_bench),
	url(r'^bench/$', views.bench)
]
