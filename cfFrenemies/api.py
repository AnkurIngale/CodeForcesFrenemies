import requests as apicalls
from django.conf import settings
from .models import User_Friend, User

def verifyHandle(handle):
    r = apicalls.get(settings.URL + 'user.info?handles=' + handle)
    rjson = r.json()
    return rjson['status'] == 'OK'

class Problem:

    def __init__(self , contestID = -1 , problemID = -1 , name = "" , tags = [] , rating = -1 , solvedBy = []):
        self.contestID = contestID
        self.problemID = problemID
        self.index = contestID + problemID
        self.name = name
        self.tags = tags
        self.rating = rating
        self.solvedBy = solvedBy
    
    def __str__(self):
        return self.contestID + self.problemID

def getSolvedProblems(handle):
    r = apicalls.get(settings.URL + 'user.status?handle=' + handle)
    json = r.json()

    if json['status'] == 'OK':
        json = json['result']
        problemSet = set()

        for eachSub in json:
            pjson = eachSub['problem']
            if eachSub['verdict'] == 'OK' and eachSub['testset'] == 'TESTS':
                # don't get problems from running contests
                try:
                    contestID = str(pjson['contestId'])
                    problemID = pjson['index']
                    problem = Problem(contestID, problemID, pjson['name'], pjson['tags'], pjson['rating'])
                    problemSet.add(problem)
                except KeyError:
                    # understand this error.
                    pass

        return [True, list(problemSet)]
    else:
        return [False, []]