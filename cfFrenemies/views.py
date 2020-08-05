from django.shortcuts import render , redirect
from django.http import HttpResponse
from django.contrib import auth , messages
from django.conf import settings
from django.db import models
from django.core.paginator import Paginator
from django.core.cache import cache
from .api import verifyHandle
from .addons import getAllProblemsNotSolvedByUserButSolvedByFriends
from .models import User, User_Friend, User_Team
from .forms import *
import jsons
import time

# Create your views here.
def index(request):
    return render(request, template_name = 'cfFrenemies/index.html')

def verify(request , handle):
    if verifyHandle(handle):
        return HttpResponse('Correct Handle')
    else:
        return HttpResponse('Incorrect Handle')

def register(request):
    if request.user.is_authenticated:
        return HttpResponse('You are logged in. Log out to register.')

    
    if request.method == 'POST':
        form = UserAdminCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = UserAdminCreationForm()
    return render(request , template_name = 'cfFrenemies/register.html',context = {'form' : form})

def login(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            handle = form.cleaned_data.get('handle')
            password = form.cleaned_data.get('password')
            user = auth.authenticate(username = handle, password = password)
 
            if user is not None:
                # correct handle and password login the user
                auth.login(request, user)
                return redirect('index')
            else:
                messages.error(request, 'Error wrong handle/password')
    
    else:
        form = LoginForm()
    return render(request, 'cfFrenemies/login.html' , context = {"form" : form})


def logout(request):
    if request.user.is_authenticated:
        handle = request.user.handle
        auth.logout(request)
        return render(request,'cfFrenemies/logout.html',context = {'handle':handle})
    else:
        return HttpResponse('No User Logged In')

def toProblem(request, contestID, problemID):
    return redirect('https://codeforces.com/contest/' + contestID + '/problem/' + problemID)

def showSolvedProblems(request):
    if request.user.is_authenticated:

        handle = request.user.handle
        problemSet = cache.get(handle)

        if not problemSet:
            data = getAllProblemsNotSolvedByUserButSolvedByFriends(request.user)
            if data[0]:

                problemSet = data[1]
                pjson = jsons.dump(problemSet)
                cache.set(handle, pjson, settings.PROBLEMS_UPDATE_TIME)
                print('Added in Cache')

            else:
                return HttpResponse('Either we could not load data or you are all caught up. Try adding more friends.')
        else:
            problemSet = jsons.load(problemSet)
            print('Retrieved from Cache')

        lowerBoundRating = request.GET.get('lbr', 0)
        if lowerBoundRating == '':
            lowerBoundRating = 0

        higherBoundRating = request.GET.get('hbr', 5000)
        if higherBoundRating == '':
            higherBoundRating = 5000
        
        filterTags = request.GET.get('tags', '')

        try:
    
            lowerBoundRating = int(lowerBoundRating)
            higherBoundRating = int(higherBoundRating)
            
            filterTags = list(set(filterTags.split('|')))
            for i in filterTags:
                if i == '':
                    filterTags.remove(i)

            to_remove = []
            for problem in problemSet:
                if problem['rating'] < lowerBoundRating or problem['rating'] > higherBoundRating:
                    to_remove.append(problem)
                else:
                    ok = False
                    if len(filterTags):
                        count = 0
                        for tag in problem['tags']:
                            if tag in filterTags:
                                count += 1
                        
                        if count == len(filterTags):
                            ok = True
                    else:
                        ok = True
                    if not ok:
                        to_remove.append(problem)

            for problem in to_remove:
                problemSet.remove(problem)

        except:
            pass

        paginator = Paginator(problemSet, per_page = 30)
        page_number = request.GET.get('page', 1)
        page = paginator.get_page(page_number)

        return render(
            request, 
            template_name = 'cfFrenemies/showsolvedproblems.html', 
            context = {
                'problemList' : page.object_list,
                'paginator': paginator
                }
            )
    else:
        return redirect('login')

def addFriend(request):
    if request.user.is_authenticated:
        friends_till_now = User_Friend.objects.filter(friend_of = request.user)
        friends_till_now = [i.friend_handle for i in friends_till_now]
        if request.method == 'POST':
            form = AddFriendForm(request.POST)
            if form.is_valid():
                handle = form.cleaned_data.get('handle')
                if request.user.handle == handle:
                    messages.error(request , 'Logged In user cannot be added.')
                    return redirect('addFriend')
                try:
                    user_friend = User_Friend.objects.get(friend_handle = handle , friend_of = request.user)
                except User_Friend.DoesNotExist:
                    friend = User_Friend(friend_handle = handle , friend_of = request.user)
                    friend.save()
                    return redirect('addFriend')
                else:
                    messages.error(request , 'Handle already added.')
                
        else:
            form = AddFriendForm()
        return render(request,template_name = 'cfFrenemies/addfriend.html',context = {'form' : form , 'friends' : friends_till_now})
    return redirect('login')

def delFriend(request , friend_handle):
    if request.user.is_authenticated:
        friend = User_Friend.objects.get(friend_handle = friend_handle , friend_of = request.user)
        friend.delete()
        return redirect('addFriend')
    return redirect('login')

def logoutnin(request):
    if request.user.is_authenticated:
        auth.logout(request)
        return redirect('login')

def createTeam(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = CreateTeamForm(request.POST)
            if form.is_valid():
                handles = [
                    form.cleaned_data.get('handle1'),
                    form.cleaned_data.get('handle2'),
                    form.cleaned_data.get('handle3')
                ]
                handles.sort()
                try:
                    user_team = User_Team.objects.get(
                        creator_user = request.user, 
                        handle1 = handles[0], 
                        handle2 = handles[1], 
                        handle3 = handles[2]
                    )
                except User_Team.DoesNotExist:
                    user_team = User_Team(
                        creator_user = request.user,
                        handle1 = handles[0],
                        handle2 = handles[1],
                        handle3 = handles[2],
                    )
                    user_team.save()
                    return redirect('createTeam')
                else:
                    messages.error(request , 'Team already created.')

        else:
            form = CreateTeamForm()
        return render(request, template_name = 'cfFrenemies/createteam.html', context = {'form': form, 'teams': User_Team.objects.all()})
    else:
        redirect('login')
    pass

def delTeam(request, handle1, handle2, handle3):
    if request.user.is_authenticated:
        team = User_Team.objects.get(
            creator_user = request.user,
            handle1 = handle1,
            handle2 = handle2,
            handle3 = handle3,
        )
        team.delete()
        return redirect('createTeam')
    return redirect('login')

