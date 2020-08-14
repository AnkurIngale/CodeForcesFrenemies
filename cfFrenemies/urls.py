from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('verify/<handle>',views.verify, name='verify'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),
    path('toproblem/<contestID>/<problemID>',views.toProblem, name='toProblem'),
    path('showunsolvedproblems/', views.showUnsolvedProblems , name = 'showUnsolvedProblems'),
    path('addfriend/', views.addFriend, name = 'addFriend'),
    path('delfriend/<friend_handle>', views.delFriend, name = 'delFriend'),
    path('logoutnin/',views.logoutnin, name = 'logoutnin'),
    path('createteam/' , views.createTeam, name = 'createTeam'),
    path('delteam?<handle2>&<handle3>/' , views.delTeam, name = 'delTeam'),
    path('showunattemptedcontests/<team_encrypted_id>' , views.showUnattemptedContests, name = 'showUnattemptedContests'),
    path('tocontest/<contestID>/',views.toContest, name='toContest'),
]