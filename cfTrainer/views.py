from django.shortcuts import render , redirect
from django.http import HttpResponse
from .api import verifyHandle
from .addons import getAllProblemsNotSolvedByUserButSolvedByFriends
from django.conf import settings
from django.db import models
from .models import User , User_Friend
from .forms import *
from django.contrib import auth , messages
import json
import time

problemDict = {}
listLastUpdated = {}

# Create your views here.
def index(request):
    return render(request, template_name = 'cfTrainer/index.html')

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

    else:
        form = UserAdminCreationForm()
    return render(request , template_name = 'cfTrainer/register.html',context = {'form' : form})

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
    return render(request, 'cfTrainer/login.html' , context = {"form" : form})


def logout(request):
    global problemDict
    global listLastUpdated

    if request.user.is_authenticated:
        handle = request.user.handle

        del problemDict[handle]
        del listLastUpdated[handle]

        auth.logout(request)
        return render(request,'cfTrainer/logout.html',context = {'handle':handle})
    else:
        return HttpResponse('No User Logged In')

def toProblem(request, contestID, problemID):
    return redirect('https://codeforces.com/contest/' + contestID + '/problem/' + problemID)

def showSolvedProblems(request):
    
    global problemDict
    global listLastUpdated

    handle = request.user.handle
    
    if request.user.is_authenticated:

        if handle not in listLastUpdated:
            listLastUpdated[handle] = 0
        if handle not in problemDict:
            problemDict[handle] = []

        current_time = time.time()
        
        if not problemDict[handle] or (current_time - listLastUpdated[handle]) > settings.PROBLEMS_UPDATE_TIME:
            data = getAllProblemsNotSolvedByUserButSolvedByFriends(request.user)

            if data[0]:
                problemDict[handle] = data[1]
                listLastUpdated[handle] = time.time()
            else:
                return HttpResponse('Either we could not load data or you are all caught up. Try adding more friends.')

        tempProbList = problemDict[handle][:]

        if request.method == 'POST':
            lowerBoundRating = request.POST.get('lbr')
            higherBoundRating = request.POST.get('hbr')

            try:
                lowerBoundRating = int(lowerBoundRating)
                higherBoundRating = int(higherBoundRating)

                to_remove = []
                for problem in tempProbList:
                    if problem.rating < lowerBoundRating or problem.rating > higherBoundRating:
                        to_remove.append(problem)
                
                for problem in to_remove:
                    tempProbList.remove(problem)
            except:
                pass
        
        print(listLastUpdated)
        return render(request, template_name = 'cfTrainer/showsolvedproblems.html', context = {'problemList' : tempProbList})
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
        return render(request,template_name = 'cfTrainer/addfriend.html',context = {'form' : form , 'friends' : friends_till_now})
    return redirect('login')

def delFriend(request , friend_handle):
    if request.user.is_authenticated:
        friend = User_Friend.objects.get(friend_handle = friend_handle , friend_of = request.user)
        friend.delete()
    return redirect('addFriend')

def logoutnin(request):
    if request.user.is_authenticated:
        auth.logout(request)
        return redirect('login')

def createTeams(request):
    pass


