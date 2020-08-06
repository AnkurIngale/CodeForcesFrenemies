from .models import User_Friend, User
from django.conf import settings
from .api import *

def getSolvedProblemsFromAllFriends(user):
    friends = User_Friend.objects.filter(friend_of = user)
    problemSolver = {}
    allProblems = set()

    for friend in friends:
        result = getSolvedProblems(friend.friend_handle)
        if result[0]:
            problemSet = result[1]
            for problem in problemSet:
                allProblems.add(problem)
                if problem.index not in problemSolver:
                    problemSolver[problem.index] = set()
                problemSolver[problem.index].add(friend.friend_handle)
    
    if len(allProblems) > 0:
        return [True, problemSolver, list(allProblems)]
    else:
        return [False, {}, []]

def getAllProblemsNotSolvedByUserButSolvedByFriends(user):

    user_problems = getSolvedProblems(str(user.handle))
    friends_problems = getSolvedProblemsFromAllFriends(user)

    if user_problems[0] and friends_problems[0]:
        user_problems = user_problems[1]
        problemSolver = friends_problems[1]
        friends_problems = friends_problems[2]
        
        to_delete = set()
        for user_prob in user_problems:
            to_delete.add(user_prob)

        for i in to_delete:
            if i.index in problemSolver:
                del problemSolver[i.index]
        
        for problem_index in problemSolver:
            problemSolver[problem_index] = list(problemSolver[problem_index])
        
        to_delete = []
        for problem in friends_problems:
            if problem.index in problemSolver:
                problem.solvedBy = problemSolver[problem.index]
            else:
                to_delete.append(problem)
        
        for problem in to_delete:
            friends_problems.remove(problem)
        
        friends_problems = sorted(friends_problems , key = lambda x : len(x.solvedBy) , reverse = True)
        return [True , friends_problems]
    return [False , []]
    