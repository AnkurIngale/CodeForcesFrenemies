from django.shortcuts import render , redirect
from django.http import HttpResponse
from django.contrib import auth , messages
from django.conf import settings
from django.db import models
from django.core.paginator import Paginator
from django.core.cache import cache
from django.core import signing
from .api import verifyHandle, getUnattemptedContests
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
        t_handle = handle + '?unsolvedproblems'

        problemSet = cache.get(t_handle)

        if not problemSet or request.GET.get('refresh', None):
            data = getAllProblemsNotSolvedByUserButSolvedByFriends(request.user)
            if data[0]:
                problemSet = jsons.dump(data[1])
                cache.set(t_handle, problemSet, settings.UPDATE_TIME)
                print('Added in Cache')
            else:
                return HttpResponse('Either we could not load data or you are all caught up. Try adding more friends.')
        else:
            print('Retrieved from Cache')

        problemSet = jsons.load(problemSet)

        try:
            lowerBoundRating = request.GET.get('lbr', 0)
            if lowerBoundRating == '':
                lowerBoundRating = 0

            higherBoundRating = request.GET.get('hbr', 5000)
            if higherBoundRating == '':
                higherBoundRating = 5000
            
            filterTags = request.GET.get('tags', '')


        
            lowerBoundRating = int(lowerBoundRating)
            higherBoundRating = int(higherBoundRating)

            print(lowerBoundRating, higherBoundRating)
            
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
            print(len(to_remove))
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
        return render(
            request, 
            template_name = 'cfFrenemies/addfriend.html', 
            context = {
                'form': form, 
                'friends': friends_till_now
                }
            )
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
                    form.cleaned_data.get('handle2'),
                    form.cleaned_data.get('handle3')
                ]
                handles.sort()

                if request.user.handle in handles:
                    messages.error(request, 'Logged In user already in team.')
                else:
                    try:
                        user_team = User_Team.objects.get(
                            creator_user = request.user, 
                            handle2 = handles[0], 
                            handle3 = handles[1]
                        )
                    except User_Team.DoesNotExist:
                        user_team = User_Team(
                            creator_user = request.user,
                            handle2 = handles[0],
                            handle3 = handles[1],
                        )
                        user_team.save()
                        return redirect('createTeam')
                    else:
                        messages.error(request , 'Team already created.')
        else:
            form = CreateTeamForm()
        
        teams = []

        for team in User_Team.objects.filter(creator_user = request.user):
            teams.append({
                'team': team,
                'encrypted': signing.dumps({'id' : team.id})
            })

        print(teams)
        return render(
            request, 
            template_name = 'cfFrenemies/createteam.html', 
            context = {
                'form': form, 
                'teams': teams
                }
            )
    else:
        redirect('login')
    pass

def delTeam(request, handle2, handle3):
    if request.user.is_authenticated:
        team = User_Team.objects.get(
            creator_user = request.user,
            handle2 = handle2,
            handle3 = handle3,
        )
        team.delete()
        return redirect('createTeam')
    return redirect('login')

def toContest(request, contestID):
    return redirect('https://codeforces.com/contest/' + contestID)

def showUnattemptedContests(request, team_encrypted_id):
    if request.user.is_authenticated:
        team_id = signing.loads(team_encrypted_id)['id']
        team = User_Team.objects.get(id = team_id)

        id = request.user.handle + str(team) + '?contestList'
        contestList = cache.get(id)

        if not contestList or request.GET.get('refresh'):
            data = getUnattemptedContests([team.creator_user.handle, team.handle2, team.handle3])
            if data[0]:
                contestList = data[1]
                cache.set(id, jsons.dump(contestList), settings.UPDATE_TIME)
                print('Added in cache')
            else:
                return HttpResponse(
                    'There might be some error or your team may have participated in all contests.' + 
                    'Try with a different team.'
                    )
        else:
            contestList = jsons.load(contestList)
            print('Retrieved from cache')

        filter_types = request.GET.get('types', '')
        filter_types = list(set(filter_types.split('|')))
        filter_types = [i.upper() for i in filter_types]

        if '' in filter_types:
            filter_types.remove('')
        
        if filter_types:
            to_delete = []
            for c_id, contest in contestList.items():
                if contest['type'] not in filter_types:
                    to_delete.append(c_id)

            for c_id in to_delete:
                del contestList[c_id]

        paginator = Paginator( list(contestList.values()), per_page = 30)
        page_number = request.GET.get('page', 1)
        page = paginator.get_page(page_number)

        return render(
            request, 
            template_name = 'cfFrenemies/showunattemptedcontests.html', 
            context = {
                'contestList': page.object_list, 
                'paginator': paginator,
                'team_encrypted': team_encrypted_id
                }
            )
    else:
        redirect('login')