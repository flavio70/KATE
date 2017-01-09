from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^$', views.power_management),
	url(r'^powerManagement/$', views.power_management),
	url(r'^powerManagementTable/$', views.power_management_table),
	url(r'^changePowerStatus/$', views.changePowerStatus),
	url(r'^changeManualStatus/$', views.changeManualStatus),
	url(r'^getScheduledTasks/$', views.getScheduledTasks),
	url(r'^deleteScheduledTasks/$', views.deleteScheduledTasks),
	url(r'^createScheduledTasks/$', views.createScheduledTasks),
	url(r'^getRackDetails/$', views.getRackDetails),
	url(r'^getRackLog/$', views.getRackLog),
	url(r'^changeRackOwner/$', views.changeRackOwner),
	url(r'^setRackStatus/$', views.setRackStatus),
	url(r'^pingIP/$', views.pingIP)
]
