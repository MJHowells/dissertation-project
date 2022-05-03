import sys

from project_main.init import db
from flask_login import UserMixin
from datetime import date
import datetime
import json

# Goals Table
class Goals(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    goals = db.Column(db.String(db.String(4294967295)))

    @staticmethod
    # Facilitates the generation of base database elements upon account creation.
    def generate_db(self):
        goals = { 
            "max_goals" : 12,
            "goals_count" : 0,
            "next_goal_id" : 0,
            "current_goals" : [

            ],
            "completed_goals" : [

            ],
            "archived_goals" : [

            ]
        }
        db.session.add(Goals(id=self.id, goals=json.dumps(goals)))
        db.session.commit()

    # Facilitates a query of the databse to get goal data.
    def get_goals(self):
        g_db = Goals.query.filter_by(id=self.id).first()
        return json.loads(g_db.goals)

    # Facilitates a query of the databse to get goal data, and then searches goal data for a specific entry.
    def get_goal_by_folder_and_id(self, goal_id):
        g_db = Goals.query.filter_by(id=self.id).first()
        goals = json.loads(g_db.goals)
        for goal in goals["current_goals"]:
            if str(goal["goal_id"]) == str(goal_id):
                return goal
        for goal in goals["archived_goals"]:
            if str(goal["goal_id"]) == str(goal_id):
                return goal
        for goal in goals["completed_goals"]:
            if str(goal["goal_id"]) == str(goal_id):
                return goal
    
    # Facilitates the addition of new goals, generating the goal object and setting its details
    def add_goal(self, title, media_type, goal_type, quantity, end_date, start_date):
        g_db = Goals.query.filter_by(id=self.id).first()
        goals = json.loads(g_db.goals)
        goal = {
            "goal_id" : goals["next_goal_id"],
            "title" : title, 
            "media_type" : media_type,
            "goal_type" : goal_type,
            "quantity" : quantity,
            "progress" : 0,
            "start_date" : "",
            "end_date" : end_date,
            "media_ids" : [],  # used for locating
            "media_value_ids" : {} # Used for calculating
        }
        if start_date == "default":
            goal["start_date"] = date.today()
        else:
            goal["start_date"] = start_date
        
        if goal_type == "num_hours":
            goal["quantity"] = {
                "hours" : quantity,
                "minutes" : 0
            }
            goal["progress"] = {
                "hours" : 0, 
                "minutes" : 0
            }
        goals["goals_count"]+=1
        goals["next_goal_id"]+=1
        goals["current_goals"].insert(0,goal)
        g_db.goals = json.dumps(goals, default=str)
        db.session.commit()
    
    # Facilitates the updating of exisiting goals, setting goal details with new values.
    def update_goal_details(self, goal_id, title, quantity, start_date, end_date):
        g_db = Goals.query.filter_by(id=self.id).first()
        goals = json.loads(g_db.goals)
        for goal in goals["current_goals"]:
            if str(goal["goal_id"]) == str(goal_id):
                goal["title"] = title
                goal["quantity"] = quantity
                goal["start_date"] = start_date
                goal["end_date"] = end_date

                if goal["goal_type"] == "num_hours":
                    goal["quantity"] = {
                    "hours" : quantity,
                    "minutes" : 0
                }
        for goal in goals["archived_goals"]:
            if str(goal["goal_id"]) == str(goal_id):
                goal["title"] = title
                goal["quantity"] = quantity
                goal["start_date"] = start_date
                goal["end_date"] = end_date

                if goal["goal_type"] == "num_hours":
                    goal["quantity"] = {
                    "hours" : quantity,
                    "minutes" : 0
                }
        for goal in goals["completed_goals"]:
            if str(goal["goal_id"]) == str(goal_id):
                goal["title"] = title
                goal["quantity"] = quantity
                goal["start_date"] = start_date
                goal["end_date"] = end_date

                if goal["goal_type"] == "num_hours":
                    goal["quantity"] = {
                    "hours" : quantity,
                    "minutes" : 0
                }

        g_db.goals = json.dumps(goals)
        db.session.commit()
    
    # Facilitates the archiving of a goal, moving it to a new folder.
    def archive_goal(self, goal_id):
        g_db = Goals.query.filter_by(id=self.id).first()
        goals = json.loads(g_db.goals)
        for goal in goals["current_goals"]:
            if int(goal["goal_id"]) == int(goal_id):
                if Goals.check_goal_finished(goal) == True:
                    temp_goal = goal
                    goals["current_goals"].remove(goal)
                    temp_goal["end_date"] = date.today()
                    goals["completed_goals"].insert(0, temp_goal)
                    goals["goals_count"]-=1
                else:
                    goals["archived_goals"].insert(0, goal)
                    goals["current_goals"].remove(goal)
                    goals["goals_count"]-=1
        g_db.goals = json.dumps(goals, default=str)
        db.session.commit()
    
    # Facilitates the unarchiving of a goal, moving it to a new folder.
    def un_archive_goal(self, goal_id):
        g_db = Goals.query.filter_by(id=self.id).first()
        goals = json.loads(g_db.goals)
        for goal in goals["archived_goals"]:
            if int(goal["goal_id"]) == int(goal_id):
                current_date = datetime.datetime.strptime(str(date.today()), "%Y-%m-%d")
                end_date = datetime.datetime.strptime(str(goal["end_date"]), '%Y-%m-%d')
                if end_date > current_date:
                    if Goals.check_goal_finished(goal) == True:
                        temp_goal = goal
                        goals["archived_goals"].remove(goal)
                        temp_goal["end_date"] = date.today()
                        goals["completed_goals"].insert(0, temp_goal)
                        g_db.goals = json.dumps(goals, default=str)
                        db.session.commit()
                        return True
                    else:
                        if goals["goals_count"] < 12:
                            goals["current_goals"].insert(0, goal)
                            goals["archived_goals"].remove(goal)
                            goals["goals_count"]+=1
                            g_db.goals = json.dumps(goals, default=str)
                            db.session.commit()
                            return True
                        else:
                            return False      

    # Facilitates the automatic completion of a goal, when its end date has passed, moving it to a new folder.
    def complete_goal(self, goal_id):
        g_db = Goals.query.filter_by(id=self.id).first()
        goals = json.loads(g_db.goals)
        for goal in goals["current_goals"]:
            if goal["goal_id"] == goal_id:
                temp_goal = goal
                goals["current_goals"].remove(goal)
                temp_goal["end_date"] = date.today()
                goals["completed_goals"].insert(0, temp_goal)
                goals["goals_count"]-=1
        g_db.goals = json.dumps(goals, default=str)
        db.session.commit()
    
    # Facilitates the chcking of a goal, to see whether it has been finished.
    def check_goal_finished(goal):
        if goal["goal_type"] == "num_hours":
            prog_mins = (int(goal["progress"]["hours"]) * 60) + (int(goal["progress"]["minutes"]))
            goal_mins = (int(goal["quantity"]["hours"]) * 60) + (int(goal["quantity"]["minutes"]))
            if prog_mins >= goal_mins:
                return True
        elif goal["goal_type"] == "num_pages" or goal["goal_type"] == "num_books" or goal["goal_type"] == "num_films" or goal["goal_type"] == "num_games":
            if int(goal["progress"]) >= int(goal["quantity"]):
                return True

    # Facilitates the checking of a goal to see its status.
    def check_goal_status(self):
        complete_goals = []
        archived_goals = []
        g_db = Goals.query.filter_by(id=self.id).first()
        goals = json.loads(g_db.goals)
        curr_date = date.today()
        for goal in goals["current_goals"]:
            current_date = datetime.datetime.strptime(str(curr_date), "%Y-%m-%d")
            end_date = datetime.datetime.strptime(str(goal["end_date"]), '%Y-%m-%d')
            if end_date < current_date:
                if goal["goal_type"] == "num_hours":
                    prog_mins = (int(goal["progress"]["hours"]) * 60) + (int(goal["progress"]["minutes"]))
                    goal_mins = (int(goal["quantity"]["hours"]) * 60) + (int(goal["quantity"]["minutes"]))
                    if prog_mins >= goal_mins:
                        complete_goals.append(goal["goal_id"])
                    else:
                        archived_goals.append(goal["goal_id"])
                elif goal["goal_type"] == "num_pages" or goal["goal_type"] == "num_books" or goal["goal_type"] == "num_films" or goal["goal_type"] == "num_games":
                    if int(goal["progress"]) >= int(goal["quantity"]):
                        complete_goals.append(goal["goal_id"])
                    else:
                        archived_goals.append(goal["goal_id"])
        for goal_id in complete_goals:
            Goals.complete_goal(self, goal_id)
        
        for goal_id in archived_goals:
            Goals.archive_goal(self, goal_id)

    # Facilitates a query of goals to get a goals id. 
    def search_goal(self, context):
        g_db = Goals.query.filter_by(id=self.id).first()
        goals = json.loads(g_db.goals)
        current = goals["current_goals"]
        out = []
        for i in current:
            if i["media_type"] == context:
                out.append(i["goal_id"])
        return out

    # Facilitates the updating of a goals progress, calculating based on media completion and details.
    def update_goal(self, media):
        Goals.check_goal_status(self)
        g_db = Goals.query.filter_by(id=self.id).first()
        goals = json.loads(g_db.goals)
        temp_progress_count = 0
        temp_progress_time = []
        
        for goal in goals["current_goals"]:
            if goal["media_type"] == media["type"]:
                for ev in media["events"]["events"]:
                    if ev["status"] == "finished":
                        start_date = datetime.datetime.strptime(goal["start_date"], '%Y-%m-%d')
                        end_date = datetime.datetime.strptime(goal["end_date"], '%Y-%m-%d')
                        media_date = datetime.datetime.strptime(str(ev["date"]), '%Y-%m-%d')
                        if start_date <= media_date and media_date <= end_date:
                            if media["media_id"] not in goal["media_ids"]:
                                goal["media_ids"].insert(0,media["media_id"])

                            if goal["goal_type"] == "num_hours":
                                temp_progress_time.append(media["length"])
                                goal["media_value_ids"][media["media_id"]] = temp_progress_time
                            elif goal["goal_type"] == "num_pages":
                                temp_progress_count += int(media["length"])
                                goal["media_value_ids"][media["media_id"]] = temp_progress_count
                            elif goal["goal_type"] == "num_books" or "num_films" or "num_games":
                                temp_progress_count+=1
                                goal["media_value_ids"][media["media_id"]] = temp_progress_count
            
                if goal["goal_type"] == "num_hours":
                    
                    goal["progress"] = {}
                    goal["progress"]["hours"] = 0
                    goal["progress"]["minutes"] = 0
                    for med in goal["media_value_ids"]:
                            for time in goal["media_value_ids"][med]:
                                media_time = time.split("h", 1)
                                goal_time = goal["progress"]
                                goal["progress"] = Goals.convert_and_add_min_hours(media_time, goal_time)

                elif goal["goal_type"] == "num_pages":
                    goal["progress"] = 0
                    for med in goal["media_value_ids"]:
                        goal["progress"] += goal["media_value_ids"][med]
                        
                elif goal["goal_type"] == "num_books" or "num_films" or "num_games": 
                    goal["progress"] = 0
                    for med in goal["media_value_ids"]:
                        goal["progress"] += goal["media_value_ids"][med]
        g_db.goals = json.dumps(goals)
        db.session.commit()

    # Facilitates the conversion of durations into the correct format.
    def convert_and_add_min_hours(media_time, goal_time):
        hours = goal_time["hours"] + int(media_time[0])
        minutes = (goal_time["minutes"] + int(media_time[1].replace("m","")))
        if (minutes >= 60):
            hours+=1
            minutes = minutes % 60
        goal_time["hours"] = hours
        goal_time["minutes"] = minutes
        return goal_time
    
    # Facilitates the conversion of durations into the correct format.
    def convert_and_remove_min_hours(media_time, goals_time):
        hours = goals_time["hours"] - int(media_time[0])
        minutes = (goals_time["minutes"] - int(media_time[1].replace("m","")))
        if (minutes < 0):
            hours-=1
            minutes = minutes % 60
        goals_time["hours"] = hours
        goals_time["minutes"] = minutes
        return goals_time

    # Facilitates the checking of exisiting media to see if it can be included in a goals progress.
    def check_exisiting_media(self, consumed_media):
        Goals.check_goal_status(self)
        g_db = Goals.query.filter_by(id=self.id).first()
        goals = json.loads(g_db.goals)
        for goal in goals["current_goals"]:
            temp_media_value_ids = {}
            temp_media_ids = []
            for media in consumed_media["media"]:
                temp_progress_count = 0
                temp_progress_time = []
                if goal["media_type"] == media["type"]:
                    for ev in media["events"]["events"]:
                        if ev["status"] == "finished":
                            start_date = datetime.datetime.strptime(goal["start_date"], '%Y-%m-%d')
                            end_date = datetime.datetime.strptime(goal["end_date"], '%Y-%m-%d')
                            media_date = datetime.datetime.strptime(str(ev["date"]), '%Y-%m-%d')
                            if start_date <= media_date and media_date <= end_date:
                                if media["media_id"] not in temp_media_ids:
                                    temp_media_ids.insert(0,media["media_id"])
                                if goal["goal_type"] == "num_hours":
                                    temp_progress_time.append(media["length"])
                                    temp_media_value_ids[media["media_id"]] = temp_progress_time
                                elif goal["goal_type"] == "num_pages":
                                    temp_progress_count += int(media["length"])
                                    temp_media_value_ids[media["media_id"]] = temp_progress_count
                                elif goal["goal_type"] == "num_books" or goal["goal_type"] == "num_films" or goal["goal_type"] == "num_games":
                                    temp_progress_count+=1
                                    temp_media_value_ids[media["media_id"]] = temp_progress_count
            goal["media_value_ids"] = temp_media_value_ids
            goal["media_ids"] = temp_media_ids
            
            if goal["goal_type"] == "num_hours":
                goal["progress"] = {}
                goal["progress"]["hours"] = 0
                goal["progress"]["minutes"] = 0
                for med in goal["media_value_ids"]:
                        for time in goal["media_value_ids"][med]:
                            media_time = time.split("h", 1)
                            goal_time = goal["progress"]
                            goal["progress"] = Goals.convert_and_add_min_hours(media_time, goal_time)

            elif goal["goal_type"] == "num_pages":
                goal["progress"] = 0
                for med in goal["media_value_ids"]:
                    goal["progress"] += goal["media_value_ids"][med]
                    
            elif goal["goal_type"] == "num_books" or "num_films" or "num_games": 
                goal["progress"] = 0
                for med in goal["media_value_ids"]:
                    goal["progress"] += goal["media_value_ids"][med]
        g_db.goals = json.dumps(goals)
        db.session.commit()

    # Returns the first goal in the database to be shown on the home page. 
    def getFirstCurrGoal(self):
        g_db = Goals.query.filter_by(id=self.id).first()
        goals = json.loads(g_db.goals)
        if len(goals["current_goals"]) != 0:
            return goals["current_goals"][0]
        else:
            return None
    

