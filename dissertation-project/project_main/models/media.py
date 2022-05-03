from project_main.init import db

import sys

import json
from flask_login import UserMixin,current_user
from datetime import date, datetime
from project_main.models.goals import Goals


# Media table
class Media(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    consumed = db.Column(db.String(4294967295), unique=False, nullable=True)    
    consuming = db.Column(db.String(4294967295), unique=False, nullable=True)
    to_consume = db.Column(db.String(4294967295), unique=False, nullable=True)
    tags = db.Column(db.String(4294967295), unique=False, nullable=True)
    next_media_id = db.Column(db.Integer)
    
    @staticmethod
    # Facilitates the generation of media table base data upon account creation.
    def new_user_media(self):
        consumed = json.dumps({
            "count" : 0,
            "media" : []
        })

        consuming = json.dumps({
            "count" : 0,
            "media" : []
        })

        to_consume = json.dumps({
            "count" : 0,
            "media" : []
        })
        
        tags = json.dumps([])

        media = Media(id=self.id, consumed=consumed, consuming=consuming, to_consume=to_consume, tags=tags, next_media_id=0)
        
        db.session.add(media)
        db.session.commit()

    # Facilitates the querying of the media database.
    def get_media(self):
        return Media.query.filter_by(id=self.id).first()
    
    # Facilitates the querying of the media database, and location of a specific media item by id.
    def filter_media_by_mediaid(m_db, media_folder, media_id):
        if media_folder == "consumed":
            m_folder = json.loads(m_db.consumed)
        elif media_folder == "consuming":
            m_folder = json.loads(m_db.consuming)
        elif media_folder == "to_consume":
            m_folder = json.loads(m_db.to_consume)

        for media in m_folder["media"]:
            if str(media["media_id"]) == str(media_id):
                return media

    # Sorts media into data order (most recent first). Dates can be changed in editing. 
    def sort_media(self):
        m_db = Media.query.filter_by(id=self.id).first()
           
        # Sort for consumed media
        consumed_media = json.loads(m_db.consumed)
        temp_media = consumed_media["media"]
        temp_media.sort(key = lambda  x:x["finished"]["date"], reverse=True)
        consumed_media["media"] = temp_media
        m_db.consumed = json.dumps(consumed_media)

        # Sort for Consuming Media
        consuming_media = json.loads(m_db.consuming)
        temp_media = consuming_media["media"]
        temp_media.sort(key = lambda  x:x["date_added"], reverse=True)
        consuming_media["media"] = temp_media
        m_db.consuming = json.dumps(consuming_media)

        # Sort for To Consume Media
        to_consume_media = json.loads(m_db.to_consume)
        temp_media = to_consume_media["media"]
        temp_media.sort(key = lambda  x:x["date_added"], reverse=True)
        to_consume_media["media"] = temp_media
        m_db.to_consume = json.dumps(to_consume_media)

        # Session Commit for All sorts
        db.session.commit()

    # Facilitates the addition of a piece of media (book), generating the media object and setting its details.
    def add_book(self, type, title, length, author, description, finished, status, fin_date, tags):
        # Function for adding tags to media object.
        temp_aut = []
        for aut in author:
            temp_aut.append(aut.replace("'", ""))
        author = temp_aut

        temp_tag = []
        for tag in tags:
            temp_tag.append(tag.replace("'", ""))
        tags = temp_tag

        def set_tags(tags, media):
            out = []
            for aut in media["author"]:
                if aut != "":
                    out.append(aut)
            for tag in tags:
                if tag != "":
                    if tag not in out:
                        out.append(tag)
            return out
        m_db = Media.query.filter_by(id=self.id).first()
        media = {
            "media_id" : m_db.next_media_id,
            "type" : type,
            "status" : status,
            "title" : title.replace("'", ""),
            "length" : length,
            "author" : author,
            "description" : description.replace("'", ""),
            "date_added" : date.today(),
            "tags" : [

            ], #List e.g. ["Fantasy, Epic, Wheel of time"]
            "finished" : {
                "status" : finished,
                "date" : ""
            },
            "events" : {
                "nextEventId" : 1,
                "events" : [

                ]
            }
        }
        
        media["tags"] = set_tags(tags, media)
        Media.update_tags(self, media["tags"])

        if any(i.isdigit() for i in length):
            media["length"] = int(length)
        else:
            media["length"] = 0

        if  status == "finished":
            event = {
            "event_id" : media["events"]["nextEventId"],
            "rating" : 0,
            "review" : "",
            "progress" : length,
            "date" : "",
            "status" : "finished" #Not sure if status should be included
            }
            media["events"]["events"].insert(0,event)
            media["events"]["nextEventId"] = media["events"]["nextEventId"] + 1
            if fin_date == "":
                media["finished"]["date"] = date.today()
                media["events"]["events"][0]["date"] = date.today()
            else:
                media["finished"]["date"] = fin_date
                media["events"]["events"][0]["date"] = fin_date
            media_temp = json.loads(m_db.consumed)
            media_temp["media"].insert(0,media)
            media_temp["count"]+=1
            m_db.consumed = json.dumps(media_temp, default=str)
        elif status == "consuming":
            media_temp = json.loads(m_db.consuming)
            media_temp["media"].insert(0,media)
            media_temp["count"]+=1
            m_db.consuming = json.dumps(media_temp, default=str)
        elif status == "to_consume":
            media_temp = json.loads(m_db.to_consume)
            media_temp["media"].insert(0,media)
            media_temp["count"]+=1
            m_db.to_consume = json.dumps(media_temp, default=str)
        m_db.next_media_id+=1
        db.session.commit()

    # Facilitates the addition of a piece of media (movie), generating the media object and setting its details.
    def add_movie(self, type, title, duration, director, actors, finished, description, status, fin_date, tags):

        temp_act = []
        for act in actors:
            temp_act.append(act.replace("'", ""))
        actors = temp_act

        temp_tag = []
        for tag in tags:
            temp_tag.append(tag.replace("'", ""))
        tags = temp_tag

        def set_tags(tags, media):
            out = []
            for aut in media["actors"]:
                if aut != "":
                    out.append(aut)
            for tag in tags:
                if tag != "":
                    if tag not in out:
                        out.append(tag)
            if director not in out:
                out.append(director)

            return out
        m_db = Media.query.filter_by(id=self.id).first()
        media = {
            "media_id" : m_db.next_media_id,
            "type" : type,
            "status" : status,
            "title" : title.replace("'", ""),
            "length" : duration,
            "director" : director.replace("'", ""),
            "actors" : actors, # list
            "description" : description.replace("'", ""),
            "date_added" : date.today(),
            "tags" : [

            ], #List e.g. ["Fantasy, Epic, Wheel of time"]
            "finished" : {
                "status" : finished,
                "date" : ""
            },
            "rating" : {
                "default" : "true",
                "average" : 0,
                "rating" : 0
            },
            "review" : "",
            "events" : {
                "nextEventId" : 1,
                "events" : [
                    
                ]
            }
        }

        media["tags"] = set_tags(tags, media)
        Media.update_tags(self, media["tags"])

        if  status == "finished":
            event = {
            "event_id" : media["events"]["nextEventId"],
            "rating" : 0,
            "review" : "",
            "progress" : duration,
            "date" : "",
            "status" : "finished" #Not sure if status should be included
            }
            media["events"]["events"].insert(0,event)
            media["events"]["nextEventId"] = media["events"]["nextEventId"] + 1
            if fin_date == "":
                media["finished"]["date"] = date.today()
                media["events"]["events"][0]["date"] = date.today()
            else:
                media["finished"]["date"] = fin_date
                media["events"]["events"][0]["date"] = fin_date
            media_temp = json.loads(m_db.consumed)
            media_temp["media"].insert(0,media)
            media_temp["count"]+=1
            m_db.consumed = json.dumps(media_temp, default=str)
        elif status == "consuming":
            media_temp = json.loads(m_db.consuming)
            media_temp["media"].insert(0,media)
            media_temp["count"]+=1
            m_db.consuming = json.dumps(media_temp, default=str)
        elif status == "to_consume":
            media_temp = json.loads(m_db.to_consume)
            media_temp["media"].insert(0,media)
            media_temp["count"]+=1
            m_db.to_consume = json.dumps(media_temp, default=str)
        m_db.next_media_id+=1
        db.session.commit()
    
    # Facilitates the addition of a piece of media (audiobook), generating the media object and setting its details.
    def add_audiobook(self, type, title, author, narators, duration, description, finished, status, fin_date, tags):
        temp_aut = []
        for aut in author:
            temp_aut.append(aut.replace("'", ""))
        author = temp_aut

        temp_nar = []
        for nar in narators:
            temp_nar.append(nar.replace("'", ""))
        narators = temp_nar

        temp_tag = []
        for tag in tags:
            temp_tag.append(tag.replace("'", ""))
        tags = temp_tag

        def set_tags(tags, media):
            out = []
            for aut in media["author"]:
                if aut != "":
                    out.append(aut)
            for tag in tags:
                if tag != "":
                    if tag not in out:
                        out.append(tag)
            return out
        m_db = Media.query.filter_by(id=self.id).first()
        media = {
            "media_id" : m_db.next_media_id,
            "type" : type,
            "status" : status,
            "title" : title.replace("'", ""), 
            "author" : author,
            "narrators" : narators, #list
            "length" : duration,
            "description" : description.replace("'", ""),
            "date_added" : date.today(),
            "tags" : [

            ], #List e.g. ["Fantasy, Epic, Wheel of time"]
            "finished" : {
                "status" : finished,
                "date" : ""
            },
            "rating" : {
                "default" : "true",
                "average" : 0,
                "rating" : 0
            },
            "review" : "",
            "events" : {
                "nextEventId" : 1,
                "events" : [
                    
                ]
            }
        }

        media["tags"] = set_tags(tags, media)
        Media.update_tags(self, media["tags"])

        if  status == "finished":
            event = {
            "event_id" : media["events"]["nextEventId"],
            "rating" : 0,
            "review" : "",
            "progress" : duration,
            "date" : "",
            "status" : "finished" #Not sure if status should be included
            }
            media["events"]["events"].insert(0,event)
            media["events"]["nextEventId"] = media["events"]["nextEventId"] + 1
            if fin_date == "":
                media["finished"]["date"] = date.today()
                media["events"]["events"][0]["date"] = date.today()
            else:
                media["finished"]["date"] = fin_date
                media["events"]["events"][0]["date"] = fin_date
            media_temp = json.loads(m_db.consumed)
            media_temp["media"].insert(0,media)
            media_temp["count"]+=1
            m_db.consumed = json.dumps(media_temp, default=str)
        elif status == "consuming":
            media_temp = json.loads(m_db.consuming)
            media_temp["media"].insert(0,media)
            media_temp["count"]+=1
            m_db.consuming = json.dumps(media_temp, default=str)
        elif status == "to_consume":
            media_temp = json.loads(m_db.to_consume)
            media_temp["media"].insert(0,media)
            media_temp["count"]+=1
            m_db.to_consume = json.dumps(media_temp, default=str)
        m_db.next_media_id+=1
        db.session.commit()
      
    # Facilitates the addition of a piece of media (video game), generating the media object and setting its details.
    def add_video_game(self, type, name, developer, genres, description, finished, status, fin_date, tags):
        temp_gen = []
        for genre in genres:
            temp_gen.append(genre.replace("'", ""))
        genres = temp_gen

        temp_tag = []
        for tag in tags:
            temp_tag.append(tag.replace("'", ""))
        tags = temp_tag

        def set_tags(tags, media):
            out = []
            for aut in media["genre"]:
                if aut != "":
                    out.append(aut)
            for tag in tags:
                if tag != "":
                    if tag not in out:
                        out.append(tag)
            if developer not in tags:
                out.append(developer)
            return out
        m_db = Media.query.filter_by(id=self.id).first()
        media = {
            "media_id" : m_db.next_media_id,
            "type" : type,
            "status" : status,
            "title" : name.replace("'", ""),
            "developer" : developer.replace("'", ""),
            "genre" : genres, #list
            "length" : None, 
            "description" : description.replace("'", ""),
            "date_added" : date.today(),
            "tags" : [

            ], #List e.g. ["Fantasy, Epic, Wheel of time"]
            "finished" : {
                "status" : finished,
                "date" : ""
            },
            "rating" : {
                "default" : "true",
                "average" : 0,
                "rating" : 0
            },
            "review" : "",
            "events" : {
                "nextEventId" : 1,
                "events" : [
                    
                ]
            }
        }

        media["tags"] = set_tags(tags, media)
        Media.update_tags(self, media["tags"])

        if  status == "finished":
            event = {
            "event_id" : media["events"]["nextEventId"],
            "rating" : 0,
            "review" : "",
            "date" : "",
            "status" : "finished" #Not sure if status should be included
            }
            media["events"]["events"].insert(0,event)
            media["events"]["nextEventId"] = media["events"]["nextEventId"] + 1
            if fin_date == "":
                media["finished"]["date"] = date.today()
                media["events"]["events"][0]["date"] = date.today()
            else:
                media["finished"]["date"] = fin_date
                media["events"]["events"][0]["date"] = fin_date
            media_temp = json.loads(m_db.consumed)
            media_temp["media"].insert(0,media)
            media_temp["count"]+=1
            m_db.consumed = json.dumps(media_temp, default=str)
        elif status == "consuming":
            media_temp = json.loads(m_db.consuming)
            media_temp["media"].insert(0,media)
            media_temp["count"]+=1
            m_db.consuming = json.dumps(media_temp, default=str)
        elif status == "to_consume":
            media_temp = json.loads(m_db.to_consume)
            media_temp["media"].insert(0,media)
            media_temp["count"]+=1
            m_db.to_consume = json.dumps(media_temp, default=str)
        m_db.next_media_id+=1
        db.session.commit()
         
    # facilitates the deletion of existing media.
    def delete_media(self, media_folder, media_index):
        def delete_func(media_index, media_temp):
            for item in media_temp["media"]:
                if str(item["media_id"]) == str(media_index):
                    media_temp["media"].remove(item)
                    media_temp["count"]-=1
                    return media_temp
        m_db = Media.query.filter_by(id=self.id).first()

        if media_folder == "consuming":
            media_temp = delete_func(media_index, json.loads(m_db.consuming))
            m_db.consuming = json.dumps(media_temp, default=str)
        elif media_folder == "consumed":
            media_temp = delete_func(media_index, json.loads(m_db.consumed))
            m_db.consumed = json.dumps(media_temp, default=str)
        elif media_folder == "to_consume":
            media_temp = delete_func(media_index, json.loads(m_db.to_consume))
            m_db.to_consume = json.dumps(media_temp, default=str)
        db.session.commit()

    # Facilitates the updating of existing media (book), updating its details.
    def update_book_details(self, media_folder, media_id, title, length, author, description, tags, add_date):
        temp_aut = []
        for aut in author:
            temp_aut.append(aut.replace("'", ""))
        author = temp_aut

        temp_tag = []
        for tag in tags:
            temp_tag.append(tag.replace("'", ""))
        tags = temp_tag

        m_db = Media.query.filter_by(id=self.id).first()
        if media_folder == "consumed":
            m_data = json.loads(m_db.consumed)
        if media_folder == "consuming":
            m_data = json.loads(m_db.consuming)
        if media_folder == "to_consume":
            m_data = json.loads(m_db.to_consume)
        for media in m_data["media"]:
            if str(media["media_id"]) == str(media_id):
                media["title"] = title.replace("'", "")
                media["length"] = length
                media["author"] = author
                media["description"] = description.replace("'", "")
                media["tags"] = tags
                media["date_added"] = add_date


        if media_folder == "consumed":
            m_db.consumed = json.dumps(m_data)
        if media_folder == "consuming":
            m_db.consuming = json.dumps(m_data)
        if media_folder == "to_consume":
            m_db.to_consume = json.dumps(m_data)
        db.session.commit()
        Media.update_tags(self, tags)

    # Facilitates the updating of existing media (movie), updating its details.
    def update_movie_details(self, media_folder, media_id, title, director, actors, description, duration, tags, add_date):

        temp_act = []
        for act in actors:
            temp_act.append(act.replace("'", ""))
        actors = temp_act

        temp_tag = []
        for tag in tags:
            temp_tag.append(tag.replace("'", ""))
        tags = temp_tag

        m_db = Media.query.filter_by(id=self.id).first()
        if media_folder == "consumed":
            m_data = json.loads(m_db.consumed)
        if media_folder == "consuming":
            m_data = json.loads(m_db.consuming)
        if media_folder == "to_consume":
            m_data = json.loads(m_db.to_consume)
        for media in m_data["media"]:
            if str(media["media_id"]) == str(media_id):
                media["title"] = title.replace("'", "")
                media["length"] = duration
                media["director"] = director.replace("'", "")
                media["actors"] = actors
                media["description"] = description.replace("'", "")
                media["tags"] = tags
                media["date_added"] = add_date


        if media_folder == "consumed":
            m_db.consumed = json.dumps(m_data)
        if media_folder == "consuming":
            m_db.consuming = json.dumps(m_data)
        if media_folder == "to_consume":
            m_db.to_consume = json.dumps(m_data)
        db.session.commit()
        Media.update_tags(self, tags)

    # Facilitates the updating of existing media (audiobook), updating its details.
    def update_audiobook_details(self, media_folder, media_id, title, authors, narrators, description, duration, tags, add_date):

        temp_aut = []
        for aut in authors:
            temp_aut.append(aut.replace("'", ""))
        authors = temp_aut

        temp_nar = []
        for nar in narrators:
            temp_nar.append(nar.replace("'", ""))
        narrators = temp_nar

        temp_tag = []
        for tag in tags:
            temp_tag.append(tag.replace("'", ""))
        tags = temp_tag

        m_db = Media.query.filter_by(id=self.id).first()
        if media_folder == "consumed":
            m_data = json.loads(m_db.consumed)
        if media_folder == "consuming":
            m_data = json.loads(m_db.consuming)
        if media_folder == "to_consume":
            m_data = json.loads(m_db.to_consume)
        for media in m_data["media"]:
            if str(media["media_id"]) == str(media_id):
                media["title"] = title.replace("'", "")
                media["length"] = duration
                media["narrators"] = narrators
                media["author"] = authors
                media["description"] = description.replace("'", "")
                media["tags"] = tags
                media["date_added"] = add_date


        if media_folder == "consumed":
            m_db.consumed = json.dumps(m_data)
        if media_folder == "consuming":
            m_db.consuming = json.dumps(m_data)
        if media_folder == "to_consume":
            m_db.to_consume = json.dumps(m_data)
        db.session.commit()
        Media.update_tags(self, tags)
    
    # Facilitates the updating of existing media (video game), updating its details.
    def update_videogame_details(self, media_folder, media_id, title, developer, genre, description, tags, add_date):

        temp_gen = []
        for gen in genre:
            temp_gen.append(gen.replace("'", ""))
        genre = temp_gen

        temp_tag = []
        for tag in tags:
            temp_tag.append(tag.replace("'", ""))
        tags = temp_tag

        m_db = Media.query.filter_by(id=self.id).first()
        if media_folder == "consumed":
            m_data = json.loads(m_db.consumed)
        if media_folder == "consuming":
            m_data = json.loads(m_db.consuming)
        if media_folder == "to_consume":
            m_data = json.loads(m_db.to_consume)
        for media in m_data["media"]:
            if str(media["media_id"]) == str(media_id):
                media["title"] = title.replace("'", "")
                media["genre"] = genre
                media["developer"] = developer.replace("'", "")
                media["description"] = description.replace("'", "")
                media["tags"] = tags
                media["date_added"] = add_date


        if media_folder == "consumed":
            m_db.consumed = json.dumps(m_data)
        if media_folder == "consuming":
            m_db.consuming = json.dumps(m_data)
        if media_folder == "to_consume":
            m_db.to_consume = json.dumps(m_data)
        db.session.commit()
        Media.update_tags(self, tags)
        
    # Facilitates the quering of media, getting media that should be deleted from goals progress.
    def get_media_for_goal_del_update(self, media_folder, media_index):
        m_db = Media.query.filter_by(id=self.id).first()
        if media_folder == "consumed":
            db_media = json.loads(m_db.consumed)
            for m in db_media["media"]:
                if str(m["media_id"]) == str(media_index):
                    return m
        # Will need updating for when events are added
        elif media_folder == "consuming":
            db_media = json.loads(m_db.consuming)
            for m in db_media["media"]:
                if str(m["media_id"]) == str(media_index):
                    return m

    # Facilitates the adition of events, generating the event object and setting its details.
    def add_event(self, media_folder, media_id, rating, review, progress):
        m_db = Media.query.filter_by(id=self.id).first()
        if media_folder == "consumed":
            media_fol = json.loads(m_db.consumed)
        elif media_folder == "consuming":
            media_fol = json.loads(m_db.consuming)
        elif media_folder == "to_consume":
            media_fol = json.loads(m_db.to_consume)
        for m in media_fol["media"]:
            if str(m["media_id"]) == str(media_id):
                event = {
                "event_id" : m["events"]["nextEventId"],
                "rating" : rating,
                "review" : review,
                "progress" : progress,
                "date" : date.today(),
                "status" : "" #Not sure if status should be included
                }
                

                if m["type"] == "book":
                    if int(progress) == int(m["length"]):
                        event["status"] = "finished"
                elif m["type"] == "movie" or "audiobook":
                    ev_time = progress.split("h", 1)
                    ev_hours = int(ev_time[0])
                    ev_minutes = int(ev_time[1].replace("m",""))
                    ev_time = (ev_hours * 60) + ev_minutes
                    
                    media_time = m["length"].split("h", 1)
                    media_hours = int(media_time[0])
                    media_minutes = int(media_time[1].replace("m", ""))
                    media_time = (media_hours * 60) + media_minutes
                    
                    if ev_time >= media_time:
                        event["status"] = "finished"



                m["events"]["events"].insert(0,event)
                m["events"]["nextEventId"] = m["events"]["nextEventId"] + 1

                #Checking if media needs to be moved
                if media_folder == "consumed":
                    if event["status"] != "finished":
                        move_status = True
                    elif event["status"] == "finished":
                        move_status = False
                elif media_folder == "consuming":
                    if event["status"] == "finished":
                        move_status = True
                    elif event["status"] != "finished":
                        move_status = False
                    

                
        if media_folder == "consumed":
            m_db.consumed = json.dumps(media_fol, default=str)
        elif media_folder == "consuming":
            m_db.consuming = json.dumps(media_fol, default=str)
        elif media_folder == "to_consume":
            m_db.to_consume= json.dumps(media_fol, default=str)

        db.session.commit()

        if move_status == True:
            if media_folder == "consumed":
                Media.move_media(self, media_id, media_folder, "consuming")
            elif media_folder == "consuming":
                Media.move_media(self, media_id, media_folder, "consumed") 

    # Facilitates the updating of events, updating the events details.
    def update_event(self, media_folder, media_id, event_id, rating, review, progress):
        m_db = Media.query.filter_by(id=self.id).first()
        if media_folder == "consumed":
            media_fol = json.loads(m_db.consumed)
        elif media_folder == "consuming":
            media_fol = json.loads(m_db.consuming)
        elif media_folder == "to_consume":
            media_fol = json.loads(m_db.to_consume)
        
        for m in media_fol["media"]:
            if str(m["media_id"]) == str(media_id):
                for event in m["events"]["events"]:
                    if str(event["event_id"]) == str(event_id):
                        event["rating"] = rating
                        event["review"] = review
                        event["progress"] = progress
                        if m["type"] == "book":
                            if int(progress) == int(m["length"]):
                                event["status"] = "finished"
                            else:
                                event["status"] = ""
                        elif m["type"] == "movie" or m["type"] ==  "audiobook":
                            ev_time = progress.split("h", 1)
                            ev_hours = int(ev_time[0])
                            ev_minutes = int(ev_time[1].replace("m",""))
                            ev_time = (ev_hours * 60) + ev_minutes
                            
                            media_time = m["length"].split("h", 1)
                            media_hours = int(media_time[0])
                            media_minutes = int(media_time[1].replace("m", ""))
                            media_time = (media_hours * 60) + media_minutes
                            
                            if ev_time >= media_time:
                                event["status"] = "finished"
                            else:
                                event["status"] = ""

                        if media_folder == "consumed":
                            if event["status"] != "finished":
                                move_status = True
                            elif event["status"] == "finished":
                                move_status = False
                        elif media_folder == "consuming":
                            if event["status"] == "finished":
                                move_status = True
                            elif event["status"] != "finished":
                                move_status = False
                                

        if media_folder == "consumed":
            m_db.consumed = json.dumps(media_fol, default=str)
        elif media_folder == "consuming":
            m_db.consuming = json.dumps(media_fol, default=str)
        elif media_folder == "to_consume":
            m_db.to_consume= json.dumps(media_fol, default=str)
        db.session.commit()

        if move_status == True:
            if media_folder == "consumed":
                Media.move_media(self, media_id, media_folder, "consuming")
            elif media_folder == "consuming":
                Media.move_media(self, media_id, media_folder, "consumed")

    # Facilitates the deletion of events. 
    def delete_event(self, media_folder, media_id, event_id):
        m_db = Media.query.filter_by(id=self.id).first()
        if media_folder == "consumed":
            media_fol = json.loads(m_db.consumed)
        elif media_folder == "consuming":
            media_fol = json.loads(m_db.consuming)
        elif media_folder == "to_consume":
            media_fol = json.loads(m_db.to_consume)
        
        for m in media_fol["media"]:
            if str(m["media_id"]) == str(media_id):
                for event in m["events"]["events"]:
                    if str(event["event_id"]) == str(event_id):
                        m["events"]["events"].remove(event)
                        
        if media_folder == "consumed":
            m_db.consumed = json.dumps(media_fol, default=str)
        elif media_folder == "consuming":
            m_db.consuming = json.dumps(media_fol, default=str)
        elif media_folder == "to_consume":
            m_db.to_consume= json.dumps(media_fol, default=str)
        db.session.commit()

    # Facilitates the quering of events from the database.
    def get_events(self, media_folder, media_id):
        m_db = Media.query.filter_by(id=self.id).first()
        if media_folder == "consumed":
            media_fol = json.loads(m_db.consumed)
        elif media_folder == "consuming":
            media_fol = json.loads(m_db.consuming)
        elif media_folder == "to_consume":
            media_fol = json.loads(m_db.to_consume)
        
        for m in media_fol:
            if str(m["media_id"]) == str(media_id):
                return m["events"]
    
    # Facilitates the quering of specific events.
    def get_specf_event(self, media_folder, media_id, event_id):
        m_db = Media.query.filter_by(id=self.id).first()
        if media_folder == "consumed":
            media_fol = json.loads(m_db.consumed)
        elif media_folder == "consuming":
            media_fol = json.loads(m_db.consuming)
        elif media_folder == "to_consume":
            media_fol = json.loads(m_db.to_consume)
        
        for m in media_fol["media"]:
            if str(m["media_id"]) == str(media_id):
                for event in m["events"]["events"]:
                    if str(event["event_id"]) == str(event_id):
                        return event

    # Faciliates the moving of media between folders, (consumed, to_consume, consuming)
    def move_media(self, media_id, original_media_folder, new_media_folder):
        m_db = Media.query.filter_by(id=self.id).first()

        # Get Media home folder
        if original_media_folder == "consumed":
            media = Media.filter_media_by_mediaid(m_db, "consumed", media_id)
            Media.delete_media(self, "consumed", media_id)
        elif original_media_folder == "consuming":
            media = Media.filter_media_by_mediaid(m_db, "consuming", media_id)
            Media.delete_media(self, "consuming", media_id)
        elif original_media_folder == "to_consume":
            media = Media.filter_media_by_mediaid(m_db, "to_consume", media_id)
            Media.delete_media(self, "to_consume", media_id)
        if len(media["events"]["events"]) == 0:
            event_temp = {
                "event_id" : media["events"]["nextEventId"],
                "rating" : "0",
                "review" : "",
                "progress" : media["length"],
                "date" : date.today(),
                "status" : "" #Not sure if status should be included
            }
            media["events"]["events"].insert(0, event_temp)

        # Get new media folder
        if new_media_folder == "consumed":
            if media["type"] == "video_game":
                if media["events"]["events"][0]["status"] == "finished":
                    event = {
                    "event_id" : media["events"]["nextEventId"],
                    "rating" : "0",
                    "review" : "",
                    "progress" : media["length"],
                    "date" : date.today(),
                    "status" : "finished" #Not sure if status should be included
                    }
                    media["events"]["events"].insert(0,event)
                    media["events"]["nextEventId"] = media["events"]["nextEventId"] + 1
                elif media["events"]["events"][0]["status"] == "":
                    pass
            
            else:
                if media["events"]["events"][0]["progress"] != media["length"]:
                    event = {
                    "event_id" : media["events"]["nextEventId"],
                    "rating" : "0",
                    "review" : "",
                    "progress" : media["length"],
                    "date" : date.today(),
                    "status" : "finished" #Not sure if status should be included
                    }

                    media["events"]["events"].insert(0,event)
                    media["events"]["nextEventId"] = media["events"]["nextEventId"] + 1
                elif media["events"]["events"][0]["progress"] == media["length"]:
                    pass
            
            media["finished"]["status"] = "true"
            media["finished"]["date"] = date.today()

            new_med_fol = json.loads(m_db.consumed)
            new_med_fol["media"].insert(0, media)
            new_med_fol["count"] += 1

            m_db.consumed = json.dumps(new_med_fol, default=str)
            m_db.next_media_id += 1
            db.session.commit()

        elif new_media_folder == "consuming":
            if media["type"] == "video_game":
                if media["events"]["events"][0]["status"] == "finished":
                    event = {
                    "event_id" : media["events"]["nextEventId"],
                    "rating" : "0",
                    "review" : "",
                    "progress" : media["length"],
                    "date" : date.today(),
                    "status" : "finished" #Not sure if status should be included
                    }
                    
                    media["events"]["events"].insert(0,event)
                    media["events"]["nextEventId"] = media["events"]["nextEventId"] + 1
                elif media["events"]["events"][0]["status"] == "":
                    pass
            
            else:
                if media["events"]["events"][0]["progress"] != media["length"]:
                    event = {
                    "event_id" : media["events"]["nextEventId"],
                    "rating" : "0",
                    "review" : "",
                    "progress" : media["length"],
                    "date" : date.today(),
                    "status" : "finished" #Not sure if status should be included
                    }

                    media["events"]["events"].insert(0,event)
                    media["events"]["nextEventId"] = media["events"]["nextEventId"] + 1
                elif media["events"]["events"][0]["progress"] == media["length"]:
                    pass

            media["finished"]["status"] = "false"
            media["finished"]["date"] = ""

            new_med_fol = json.loads(m_db.consuming)
            new_med_fol["media"].insert(0, media)
            new_med_fol["count"] += 1

            m_db.consuming = json.dumps(new_med_fol, default=str)
            m_db.next_media_id += 1
            db.session.commit()
        elif new_media_folder == "to_consume":
            event = {
                "event_id" : media["events"]["nextEventId"],
                "rating" : "",
                "review" : "",
                "progress" : 0,
                "date" : date.today(),
                "status" : "" #Not sure if status should be included
                }

            media["finished"]["status"] = "false"
            media["finished"]["date"] = ""

            media["events"]["events"].insert(0,event)
            media["events"]["nextEventId"] = media["events"]["nextEventId"] + 1

            new_med_fol = json.loads(m_db.to_consume)
            new_med_fol["media"].insert(0, media)
            new_med_fol["count"] += 1
            m_db.to_consume = json.dumps(new_med_fol, default=str)
            m_db.next_media_id += 1
            db.session.commit()
        
    def move_media_on_event(self, media_id, original_media_folder, new_media_folder):
        
        return

    # Facilitates the adding of tags based on media contents.
    def update_tags(self, media_tags):
        m_db = Media.query.filter_by(id=self.id).first()
        tags = json.loads(m_db.tags)
        for tag in media_tags:
            if tag not in tags:
                tags.insert(0,tag)
        m_db.tags = json.dumps(tags)
        db.session.commit()

    # Facilitates the querying of media items for goal updates.
    def get_media_for_goal_del_update(self, media_folder, media_index):
        m_db = Media.query.filter_by(id=self.id).first()
        if media_folder == "consumed":
            db_media = json.loads(m_db.consumed)
            for m in db_media["media"]:
                if str(m["media_id"]) == str(media_index):
                    return m
        # Will need updating for when events are added
        elif media_folder == "consuming":
            db_media = json.loads(m_db.consuming)
            for m in db_media["media"]:
                if str(m["media_id"]) == str(media_index):
                    return m

    # Facilitates the adding of tags based on media contents.
    def update_tags(self, media_tags):
        m_db = Media.query.filter_by(id=self.id).first()
        tags = json.loads(m_db.tags)
        for tag in media_tags:
            if tag not in tags:
                tags.insert(0,tag)
        m_db.tags = json.dumps(tags)
        db.session.commit()

    # Returns the first piece of media in the database to be shown on the home page. 
    def getFirstConsuming(self):
        m_db = Media.query.filter_by(id=self.id).first()
        media_fol = json.loads(m_db.consuming)
        if len(media_fol["media"]) != 0:
            return media_fol["media"][0]
        else: 
            return None

    