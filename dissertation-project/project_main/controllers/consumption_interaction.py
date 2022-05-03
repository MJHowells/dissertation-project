from threading import currentThread
from flask import Blueprint, render_template, redirect, url_for
from flask.globals import request
from flask_login import current_user
from project_main.init import db
import json
import sys
from flask.helpers import flash


from project_main.models.account import User
from project_main.models.media import Media
from project_main.models.goals import Goals
from project_main.forms.media_forms import new_media_form

consumption_interaction = Blueprint('consumption_interaction', __name__, template_folder='../views/')

# This file contains functions which render and control media interaction functions.

# Renders add new media page and facilitates the addition of new media upon succesful post request. 
@consumption_interaction.route('/add_new_media', methods=['GET','POST'])
def add_new_media():
    if current_user.is_authenticated:   
        media_types = User.get_media_types(current_user)
        media = Media.get_media(current_user)
        user_tags = media.tags
        if request.method == "POST":
            type = request.form['type_select']
            
            if type == "book":
                title = request.form.get("title")
                length = request.form.get("pages")
                author = request.form.getlist("author")
                description = request.form.get("description")
                status = request.form['status_select']
                tags = request.form.getlist("tag")
                if status == "finished":
                    finished = True
                else:
                    finished = False
                
                if finished == True:
                    specDate = request.form.get("fin_date_check")
                    if specDate == "choose_date":
                        fin_date = request.form.get("fin_date")
                    else:
                        fin_date = ""
                else:
                    fin_date = ""
                Media.add_book(current_user, type, title, length, author, description, finished, status, fin_date, tags)
            elif type == "movie":
                dur_hour = request.form.get("duration_hour")
                dur_min = request.form.get("duration_min")
                duration = dur_hour + "h " + dur_min + "m"
                title = request.form.get("title")
                director = request.form.get("director")
                actors = request.form.getlist("actor")
                status = request.form['status_select']
                tags = request.form.getlist("tag")
                if status == "finished":
                    finished = True
                else:
                    finished = False
                if finished == True:
                    specDate = request.form.get("fin_date_check")
                    if specDate == "choose_date":
                        fin_date = request.form.get("fin_date")
                    else:
                        fin_date = ""
                else:
                    fin_date = ""
                description = request.form.get("description")
                Media.add_movie(current_user, type, title, duration, director, actors, finished, description, status, fin_date, tags)
            elif type == "audiobook":
                dur_hour = request.form.get("duration_hour")
                dur_min = request.form.get("duration_min")
                duration = dur_hour + "h " + dur_min + "m"
                status = request.form['status_select']
                if status == "finished":
                    finished = True
                else:
                    finished = False
                title = request.form.get("title")
                author = request.form.getlist("author")
                narators = request.form.getlist("narator")
                description = request.form.get("description")
                tags = request.form.getlist("tag")
                if finished == True:
                    specDate = request.form.get("fin_date_check")
                    if specDate == "choose_date":
                        fin_date = request.form.get("fin_date")
                    else:
                        fin_date = ""
                else:
                    fin_date = ""
                Media.add_audiobook(current_user, type, title, author, narators, duration, description, finished, status, fin_date, tags)
            elif type == "video_game":
                name = request.form.get("name_form")
                developer = request.form.get("developer")
                genre = request.form.getlist("genre")
                description = request.form.get("description")
                status = request.form['status_select']
                tags = request.form.getlist("tag")
                if status == "finished":
                    finished = True
                else:
                    finished = False
                if finished == True:
                    specDate = request.form.get("fin_date_check")
                    if specDate == "choose_date":
                        fin_date = request.form.get("fin_date")
                    else:
                        fin_date = ""
                else:
                    fin_date = ""
                Media.add_video_game(current_user, type, name, developer, genre, description, finished, status, fin_date, tags)
                
                Media.sort_media(current_user)
            flash("Media Added!")
            m_db = Media.get_media(current_user)
            consumed_media = json.loads(m_db.consumed)
            Goals.check_exisiting_media(current_user, consumed_media)
            return redirect(url_for('home.home_page')) 
        return render_template('add_new_media.html', user_tags=user_tags, media=media, media_types=media_types)
    return redirect(url_for('home.index'))

# Facilitates the deletion of media.
@consumption_interaction.route('/delete/<media_folder>/<media_index>')
def delete_media_action(media_folder, media_index):
    Media.delete_media(current_user, media_folder, media_index)
    Media.sort_media(current_user)
    m_db = Media.get_media(current_user)
    consumed_media = json.loads(m_db.consumed)
    Goals.check_exisiting_media(current_user, consumed_media)
    flash("Media Deleted!")
    return redirect(url_for('home.home_page')) 

# Facilitates the archiving of goals.
@consumption_interaction.route('/archive_goal/<goal_id>')
def archive_goal_action(goal_id):
    Goals.archive_goal(current_user, goal_id)
    flash("Goal Moved to Completed Goals or Archived Goals.")
    return redirect(url_for("consumption_interaction.view_goals"))

# Facilitates the un-archiving of goals.
@consumption_interaction.route('/un_archive_goal/<goal_id>')
def un_archive_goal_action(goal_id):
    if Goals.un_archive_goal(current_user, goal_id) == True:
        flash("Goal Un-Archived and Moved to Current Goals or Completed Goals!")
    else:
        flash("Goal Cannot be Un-Archived! Either End Date Has Passed OR To Many Current Goals.")
    return redirect(url_for("consumption_interaction.view_goals"))

# Renders create goal page and facilitates the creation of new goals upon succesful post request.
@consumption_interaction.route('/create_goal', methods=['GET','POST'])
def create_goal():
    if current_user.is_authenticated:
        media_types = User.get_media_types(current_user)
        if request.method == "POST":
            type = request.form['type_select']
            title = request.form.get("title")
            goal_type = request.form.get("goal_type")
            quantity = request.form.get("goal_ammount")
            if (request.form.get("end_date_check")):
                end_date = request.form.get("enddateForm")
            else:
                end_date = "2099-01-01"
            if (request.form.get("start_date_check")):
                start_date = request.form.get("startdateForm")
            else:
                start_date = "default"
            Goals.add_goal(current_user, title=title, media_type=type, goal_type=goal_type, quantity=quantity, end_date=end_date, start_date=start_date)
            media = Media.get_media(current_user)
            consumed = json.loads(media.consumed)
            Goals.check_exisiting_media(current_user, consumed)
            flash("Goal Created!")
            return redirect(url_for('home.home_page')) 
        return render_template('create_goal.html', media_types=media_types)
    return redirect(url_for('home.index'))

# Renders edit media page and facilitates the editing of media upon succesful post request.
@consumption_interaction.route('/edit_book/<media_folder>/<media_id>', methods=['GET', 'POST'])
def edit_media(media_folder, media_id):
    if current_user.is_authenticated:
        m_db = Media.get_media(current_user)
        media = Media.filter_media_by_mediaid(m_db, media_folder, media_id)
        user_tags = json.loads(m_db.tags)
        type = media["type"]
        if type == "movie" or type == "audiobook":
            duration = []
            media_time = media["length"].split("h",1)
            duration.append(int(media_time[0]))
            duration.append(int(media_time[1].replace("m","")))  
        elif type == "music":
            duration = []
            media_time = media["length"].split("m",1)
            duration.append(int(media_time[0]))
            duration.append(int(media_time[1].replace("s",""))) 
        else:
            duration = [];  
        
        if request.method == "POST":
            if type == "book":
                title = request.form.get("title")
                length = request.form.get("pages")
                author = request.form.getlist("author")
                description = request.form.get("description")
                tags = request.form.getlist("tag")
                add_date = request.form.get("add_date")
                Media.update_book_details(current_user, media_folder, media_id, title, length, author, description, tags, add_date)
            elif type == "movie":
                title = request.form.get("title")
                director = request.form.get("director")
                dur_hour = request.form.get("hours")
                dur_min = request.form.get("minutes")
                duration = dur_hour + "h " + dur_min + "m"
                actors = request.form.getlist("actor")
                description = request.form.get("description")
                tags = request.form.getlist("tag")
                add_date = request.form.get("add_date")
                Media.update_movie_details(current_user, media_folder, media_id, title, director, actors, description, duration, tags, add_date)
            elif type == "audiobook":
                title = request.form.get("title")
                authors = request.form.getlist("author")
                narrators = request.form.getlist("narrator")
                dur_hour = request.form.get("hours")
                dur_min = request.form.get("minutes")
                duration = dur_hour + "h " + dur_min + "m"
                description = request.form.get("description")
                tags = request.form.getlist("tag")
                add_date = request.form.get("add_date")
                Media.update_audiobook_details(current_user, media_folder, media_id, title, authors, narrators, description, duration, tags, add_date)
            elif type == "video_game":
                title = request.form.get("title")
                genre = request.form.getlist("genre")
                developer = request.form.get("developer")
                description = request.form.get("description")
                tags = request.form.getlist("tag")
                add_date = request.form.get("add_date")
                Media.update_videogame_details(current_user, media_folder, media_id, title, developer, genre, description, tags, add_date)
            Media.sort_media(current_user)
            m_db = Media.get_media(current_user)
            consumed_media = json.loads(m_db.consumed)
            Goals.check_exisiting_media(current_user, consumed_media)
            flash("Media Updated")
            return redirect(url_for('home.home_page')) 
        return render_template('edit_media.html', media=media, user_tags=user_tags, duration=duration)
    return redirect(url_for('home.index'))

# Renders edit goal page and facilitates the editing of goals upon succesful post request.
@consumption_interaction.route('/edit_goal/<goal_id>', methods=["GET","POST"])
def edit_goal(goal_id):
    if current_user.is_authenticated:
        goal = Goals.get_goal_by_folder_and_id(current_user, goal_id)
        start_date = goal["start_date"]
        end_date = goal["end_date"]
        if request.method == "POST":
            title = request.form.get("title")
            quantity = request.form.get("goal_ammount")
            start_date = request.form.get("startDateForm")
            end_date = request.form.get("endDateForm")
            Goals.update_goal_details(current_user, goal_id, title, quantity, start_date, end_date)
            m_db = Media.get_media(current_user)
            consumed = json.loads(m_db.consumed)
            Goals.check_exisiting_media(current_user, consumed)
            flash("Goal Updated")
            return redirect(url_for("consumption_interaction.view_goals"))
        return render_template("edit_goal.html", goal=goal, start_date=start_date, end_date=end_date)
    return redirect(url_for("home.index"))

# Renders the view goals page.
@consumption_interaction.route('/view_goals')
def view_goals():
    if current_user.is_authenticated:
        goals = Goals.get_goals(current_user)
        media = Media.get_media(current_user)
        consumed = json.loads(media.consumed)
        Goals.check_goal_status(current_user)
        return render_template('view_goals.html', goals=goals, consumed=consumed)
    return redirect(url_for('home.index'))

# Renders the view media page for consumed media.
@consumption_interaction.route('/media_home/consumed')
def view_media_consumed():
    if current_user.is_authenticated:
        media_types = User.get_media_types(current_user)
        media = Media.get_media(current_user)
        consumed = json.loads(media.consumed)
        tags = json.loads(media.tags)
        return render_template('view_media/view_media_consumed.html', consumed=consumed, tags=tags, media_types=media_types)
    return redirect(url_for('home.index'))

# Renders the view media page for consuming media.
@consumption_interaction.route('/media_home/consuming')
def view_media_consuming():
    if current_user.is_authenticated:
        media_types = User.get_media_types(current_user)
        media = Media.get_media(current_user)
        consuming = json.loads(media.consuming)
        tags = json.loads(media.tags)
        return render_template('view_media/view_media_consuming.html', consuming=consuming, tags=tags, media_types=media_types)
    return redirect(url_for('home.index'))

# Renders the view media page for to_consume media.
@consumption_interaction.route('/media_home/to_consume')
def view_media_to_consume():
    if current_user.is_authenticated:
        media_types = User.get_media_types(current_user)
        media = Media.get_media(current_user)
        to_consume = json.loads(media.to_consume)
        tags = json.loads(media.tags)
        return render_template('view_media/view_media_to_consume.html', to_consume=to_consume, tags=tags, media_types=media_types)
    return redirect(url_for('home.index'))
        
# Renders the view specific media page for specified pieces of media.
@consumption_interaction.route('/view/<media_folder>/<media_id>', methods=["GET", "POST"])
def view_specific_media(media_folder, media_id):
    if current_user.is_authenticated:
        m_db = Media.get_media(current_user)
        media = Media.filter_media_by_mediaid(m_db, media_folder, media_id)
        if request.method == "POST":
            new_media_folder = request.form.get("new_media_folder")
            Media.move_media(current_user, media_id, media_folder, new_media_folder)
            flash("Media moved to " + new_media_folder + "!")
            Media.sort_media(current_user)
            return redirect(url_for('consumption_interaction.view_specific_media',media_folder=new_media_folder, media_id=media_id))
        return render_template('view_media/view_specific_media.html', media=media, media_folder=media_folder)
    return redirect(url_for('home.index'))

# Renders the view specific goal page for specific pieces goals.
@consumption_interaction.route('/view/goal/<goal_id>')
def view_specific_goal(goal_id):
    if current_user.is_authenticated:
        goal = Goals.get_goal_by_folder_and_id(current_user, goal_id)
        media = Media.get_media(current_user)
        consumed = json.loads(media.consumed)
        return render_template('show_details_goal.html', goal=goal, consumed=consumed)
    return redirect(url_for('home.index'))

# Renders add event page, facilitating the addition of new events upon succesful post request.
@consumption_interaction.route('/add_event/<media_folder>/<media_id>', methods=["GET", "POST"])
def add_event(media_folder, media_id):
    if current_user.is_authenticated:
        m_db = Media.get_media(current_user)
        media = Media.filter_media_by_mediaid(m_db, media_folder, media_id)
        if request.method == "POST":

            rating = request.form.get("rating")
            review = request.form.get("review")
            progress = request.form.get("progress")
            if media["type"] == "audiobook" or media["type"] == "movie":
                dur_min = request.form.get("hour")
                dur_sec = request.form.get("min")
                progress = dur_min + "h " + dur_sec + "m"
 
            Media.add_event(current_user, media_folder, media_id, rating, review, progress)

            if media_folder == "consumed":
                temp_media = json.loads(m_db.consumed)
                Goals.check_exisiting_media(current_user, temp_media)

            if progress == media["length"]:
                flash("Event Added and Moved to Valid Folder")
                return redirect(url_for("consumption_interaction.view_specific_media",media_folder="consumed", media_id=media_id))
            elif progress != media["length"]:
                if media_folder == "consumed":
                    flash("Event Added and Moved to Valid Folder")
                    return redirect(url_for("consumption_interaction.view_specific_media",media_folder="consuming", media_id=media_id))
                elif media_folder == "consuming":
                    flash("Event Added")
                    return redirect(url_for("consumption_interaction.view_specific_media",media_folder=media_folder, media_id=media_id))

            # return redirect(url_for("consumption_interaction.view_specific_media",media_folder=media_folder, media_id=media_id))
        return render_template("add_event.html", media=media, media_folder=media_folder)
    return redirect(url_for("home.index"))

# Renders the edit event page, facilitating the editing of existing events upon succesful post request.
@consumption_interaction.route('/edit_event/<media_folder>/<media_id>/<event_id>', methods=["GET", "POST"])
def edit_event(media_folder, media_id, event_id):
    if current_user.is_authenticated:
        m_db = Media.get_media(current_user)
        media = Media.filter_media_by_mediaid(m_db, media_folder, media_id)
        event = Media.get_specf_event(current_user, media_folder, media_id, event_id)
        if media["type"] == "movie" or media["type"] == "audiobook":
            temp_time = event["progress"].split("h", 1)
            hours = (temp_time[0])
            minutes = temp_time[1].replace("m","")
            minutes = int(minutes.replace(" ", ""))
        else:
            hours = 0
            minutes = 0
        if request.method == "POST":
            rating = request.form.get("rating")
            review = request.form.get("review")
            progress = request.form.get("progress")
            

            if media["type"] == "audiobook" or media["type"] ==  "movie":
                dur_min = request.form.get("hour")
                dur_sec = request.form.get("min")
                progress = dur_min + "h " + dur_sec + "m"
            Media.update_event(current_user, media_folder, media_id, event_id, rating, review, progress)
            temp_media = json.loads(m_db.consumed)
            Goals.check_exisiting_media(current_user, temp_media)

            if progress == media["length"]:
                flash("Event Updated and Moved to Valid Folder")
                return redirect(url_for("consumption_interaction.view_specific_media",media_folder="consumed", media_id=media_id))
            elif progress != media["length"]:
                if media_folder == "consumed":
                    flash("Event Updated and Moved to Valid Folder")
                    return redirect(url_for("consumption_interaction.view_specific_media",media_folder="consuming", media_id=media_id))
                elif media_folder == "consuming":
                    flash("Event Updated")
                    return redirect(url_for("consumption_interaction.view_specific_media",media_folder=media_folder, media_id=media_id))
            

            # return redirect(url_for("consumption_interaction.view_specific_media",media_folder=media_folder, media_id=media_id))
        return render_template("edit_event.html", event=event, media=media, hours=hours, minutes=minutes)
    return redirect(url_for("home.index"))

# Facilitates the deletion of existing events.
@consumption_interaction.route('/delete_event_action/<media_folder>/<media_id>/<event_id>')
def delete_event_action(media_folder, media_id, event_id):
    if current_user.is_authenticated:
        Media.delete_event(current_user, media_folder, media_id, event_id)
        m_db = Media.get_media(current_user)
        temp_media = json.loads(m_db.consumed)
        Goals.check_exisiting_media(current_user, temp_media)
        flash("Event Deleted")
        return redirect(url_for("consumption_interaction.view_specific_media",media_folder=media_folder, media_id=media_id))

# Renders the view visualisations page.
@consumption_interaction.route(('/view_media/view_visualisations'))
def view_visualisations():
    if current_user.is_authenticated:
        Media.sort_media(current_user)
        m_db = Media.get_media(current_user)
        media = json.loads(m_db.consumed)
        cons_media = json.loads(m_db.consuming)
        to_cons_media = json.loads(m_db.to_consume)
        user_media_type = User.get_media_types(current_user)
        return render_template("visualise_media.html", media=media, user_media_type=user_media_type, cons_media=cons_media, to_cons_media=to_cons_media)
    return redirect(url_for("home.index"))