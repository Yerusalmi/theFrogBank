from django.conf.urls import url
from django.contrib.auth import logout, login

from . import views


app_name = 'ebank'
urlpatterns = [

    url(r'^$', views.index, name='index'),
    url(r'^login_in/$', views.login_in, name='login In'),
url(r'^auth_view/$', views.auth_view, name='auth view'),
url(r'^logout/$', views.logout, name='logout'),
url(r'^loggedin/$', views.loggedin, name='loggedin'),
url(r'^invalid_login/$', views.invalid_login, name='invalid login'),
url(r'^signup/$', views.signup, name='signup'),
url(r'^sendmoney/$', views.sendmoney, name='sendmoney'),
url(r'^create_new_account/$', views.create_new_account, name='create new account'),
url(r'^currchange/$', views.loggedin, name='ajax post'),
url(r'^removeacc/$', views.removeacc, name='remove acc'),
url(r'^activeacc/$', views.activeacc, name='active acc'),
url(r'^history/$', views.history, name='transactions'),
url(r'^loan/$', views.loan, name='loan'),
url(r'^loanhis/$', views.loanhis, name='loan_history'),



]