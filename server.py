from flask import Flask, render_template, request, redirect, url_for, flash, session
import database_data_manager
import connection

app = Flask(__name__)
app.config["IMAGE_UPLOADS"] = "static/images/"
app.secret_key = b'$2b$12$Irdd6Ahm4DEcnmKlkvpnceJLIHZ6IxXxW6KUyquUvyvS3IVTiaRae'


@app.route("/")
def index():
    latest_questions = database_data_manager.get_latest_questions()
    return render_template("index.html", questions=latest_questions)


@app.route("/list")
def display_questions():
    order_by = request.args.get('order_by', default="submission_time")
    order_direction = request.args.get('order_direction', default="DESC")
    sorted_data = database_data_manager.sort_questions(order_by, order_direction)
    headers = connection.return_table_headers("question")
    return render_template("list.html", table_headers=headers, questions=sorted_data, selected_header=order_by)


@app.route("/question/<int:question_id>")
def qa_display(question_id):
    selected_question = database_data_manager.get_single_question(question_id)
    answers = database_data_manager.get_answers(question_id)
    tags = database_data_manager.tags_for_question(question_id)
    question_comments = database_data_manager.get_question_comment(question_id)
    answer_comments = database_data_manager.get_answer_comment()
    if selected_question is None:
        return redirect(url_for("index"))
    else:
        return render_template("question_id.html", question=selected_question, answers=answers, tags=tags,
                               question_comments=question_comments, answer_comments=answer_comments)


@app.route("/add-question/")
def add_question_form():
    headers = connection.return_table_headers("question")
    new_question = connection.create_new_record(headers)
    return render_template("add-edit-question-form.html", question=new_question)


@app.route("/list", methods=["POST"])
def add_question():
    new_question = dict(request.form)
    image = request.files["image"]
    new_question = connection.save_photo(new_question, image)
    database_data_manager.add_question(new_question)
    return redirect(url_for("display_questions"))


@app.route("/update_question/<question_id>")
def edit_question_form(question_id):
    question = database_data_manager.get_single_question(question_id)
    return render_template("add-edit-question-form.html", question=question)


@app.route("/edit-question/", methods=["POST"])
def edit_question():
    updated_question = dict(request.form)
    image = request.files["image"]
    updated_question = connection.save_photo(updated_question, image)
    database_data_manager.update_question(updated_question)
    return redirect(url_for("display_questions"))


@app.route("/question/<int:question_id>/delete")
def delete_question_confirmation(question_id):
    return render_template("delete_question.html", q_check_id=question_id)


@app.route("/question-deleted", methods=["POST"])
def delete_question():
    question_id = dict(request.form)["id"]
    database_data_manager.remove_question(question_id)
    return redirect(url_for("display_questions"))


@app.route("/question/<int:question_id>/add-answer")
def add_new_answer_form(question_id):
    question_list = database_data_manager.get_questions()
    question_to_form = []
    for elem in question_list:
        id_elem = elem["id"]
        if id_elem == question_id:
            question_to_form = elem
    return render_template("add-answer-form.html", question_to_form=question_to_form)


@app.route("/added", methods=["POST"])
def add_answer():
    new_answer = dict(request.form)
    database_data_manager.add_answer(new_answer)
    return redirect(url_for("display_questions"))


@app.route("/update_answer/<answer_id>")
def edit_answer_form(answer_id):
    answer = database_data_manager.get_single_answer(answer_id)
    return render_template("edit-answer-form.html", answer=answer)


@app.route("/edit-answer/", methods=["POST"])
def edit_answer():
    updated_answer = dict(request.form)
    image = request.files["image"]
    updated_answer = connection.save_photo(updated_answer, image)
    database_data_manager.update_answer(updated_answer)
    return redirect(url_for("display_questions"))


@app.route("/answer/<answer_id>/delete")
def delete_answer_form(answer_id):
    answer = database_data_manager.get_single_answer(answer_id)
    return render_template("delete-answer.html", answer_id=answer_id, answer=answer)


@app.route("/answer/<answer_id>/function")
def delete_answer(answer_id):
    question = database_data_manager.get_question_id_by_answer_id(answer_id)
    database_data_manager.delete_answer(answer_id)
    return redirect(url_for("qa_display", question_id=question['question_id']))


@app.route("/answer/<answer_id>/vote_up")
def vote_up(answer_id):
    question = database_data_manager.get_question_id_by_answer_id(answer_id)
    database_data_manager.vote_answer(answer_id, "Up")
    print(question)
    return redirect(url_for("qa_display", question_id=question['question_id']))


@app.route("/answer/<answer_id>/vote_down")
def vote_down(answer_id):
    question = database_data_manager.get_question_id_by_answer_id(answer_id)
    database_data_manager.vote_answer(answer_id, "Down")
    return redirect(url_for("qa_display", question_id=question['question_id']))


@app.route("/search")
def display_searched():
    searched_phrase = request.args.get('search')
    search_result = database_data_manager.get_searched(searched_phrase)
    search_result_answers = database_data_manager.get_searched_answers(searched_phrase)
    return render_template("search.html", sought_phrase=searched_phrase, questions=search_result,
                           answers=search_result_answers)


@app.route("/question/<int:question_id>/new-tag")
def add_new_tag(question_id):
    tags = database_data_manager.get_tag()
    return render_template("add-tag-form.html", tags=tags, question_id=question_id)


@app.route("/added-tag", methods=["POST"])
def add_tag():
    tag_post = dict(request.form)
    if "tags" in tag_post:
        id = database_data_manager.get_id_tag(tag_post["tags"])
        database_data_manager.add_question_tag(tag_post["question_id"], id["id"])
    elif "name" in tag_post:
        database_data_manager.add_tag(tag_post["name"])
        id = database_data_manager.get_id_tag(tag_post["name"])
        database_data_manager.add_question_tag(tag_post["question_id"], id["id"])
    return redirect(url_for("qa_display", question_id=tag_post["question_id"]))


@app.route("/tags")
def display_tags():
    tags = database_data_manager.get_tag()
    selected_tag = request.args.get('tags')
    if selected_tag is None:
        pass
    else:
        tag_id = database_data_manager.get_id_tag(selected_tag)
        how_many_tags_data = len(database_data_manager.count_tags(tag_id["id"]))
        return render_template("tags.html", tags=tags, selected_tag=f"Tag \"{selected_tag}\" was used {how_many_tags_data} times")
    return render_template("tags.html", tags=tags, selected_tag="No tag selected")


@app.route("/question/<question_id>/vote_up")
def vote_question_up(question_id):
    database_data_manager.vote_up(question_id)
    return redirect(url_for("display_questions"))


@app.route("/question/<question_id>/vote_down")
def vote_question_down(question_id):
    database_data_manager.vote_down(question_id)
    return redirect(url_for("display_questions"))


@app.route("/question/<question_id>/new-comment")
def add_comment_to_question_form(question_id):
    return render_template("add_comment_form.html", question_id=question_id)


@app.route("/comment-added", methods=["POST"])
def add_comment_to_question():
    new_comment = dict(request.form)
    int(new_comment["question_id"])
    database_data_manager.add_comment_to_question(new_comment)
    return redirect(url_for("display_questions"))


@app.route("/answer/<answer_id>/new-comment")
def add_comment_to_answer_form(answer_id):
    return render_template("add_comment_to_answer.html", answer_id=answer_id)


@app.route("/answer_comment_added", methods=["POST"])
def add_comment_to_answer():
    new_comment = dict(request.form)
    database_data_manager.add_comment_to_answer(new_comment)
    return redirect(url_for("display_questions"))


@app.route("/comment/<comment_id>/edit")
def edit_comment_form(comment_id):
    comment = database_data_manager.get_comment(comment_id)
    return render_template("edit-comment-form.html", comment=comment)


@app.route("/edit-comment", methods=["POST"])
def edit_comment():
    updated_comment = dict(request.form)
    if updated_comment["edited_count"] != "None":
        updated_comment["edited_count"] = int(updated_comment["edited_count"])
        updated_comment["edited_count"] += 1
    else:
        updated_comment["edited_count"] = 1
    database_data_manager.update_comment(updated_comment)
    return redirect(url_for("display_questions"))


@app.route("/delete_tag/<tag_id>/<question_id>")
def delete_tag(tag_id, question_id):
    database_data_manager.delete_question_tag(tag_id)
    return redirect(url_for("qa_display", question_id=question_id))


@app.route("/comments/<comment_id>/delete")
def delete_comment_form(comment_id):
    comment = database_data_manager.get_comment(comment_id)
    if comment['question_id'] is None:
        q_id = database_data_manager.get_question_id_by_answer_id(comment['answer_id'])
        question_id = q_id['question_id']
    else:
        question_id = comment['question_id']

    return render_template("delete_comment_form.html", comment_id=comment_id, question_id=question_id)


@app.route("/comments/<comment_id>/deleted")
def delete_comment(comment_id):
    comment = database_data_manager.get_comment(comment_id)
    if comment['question_id'] is None:
        q_id = database_data_manager.get_question_id_by_answer_id(comment['answer_id'])
        question_id = q_id['question_id']
    else:
        question_id = comment['question_id']

    database_data_manager.delete_comment(comment_id)

    return redirect(url_for("qa_display", question_id=question_id))


@app.route("/registered", methods=['POST'])
def register_user():
    if request.method == 'POST':
        user_name = request.form['username']
        user_password = connection.hash_password(request.form["password"])
        registered_users = database_data_manager.check_user(user_name)
        if registered_users is None:
            database_data_manager.add_new_user(user_name, user_password)
            flash("You have been successfully registered!")
            return redirect(url_for("index"))
        else:
            flash('There is a user registered with that email already!')
    return redirect(url_for("index"))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user_email = database_data_manager.check_user(email)

        if user_email is not None:
            hashed_pw = database_data_manager.get_password(email)["password_digest"]
            if connection.check_password(password, hashed_pw):
                session['username'] = user_email['username']
                return redirect(url_for("index"))

        return render_template('login.html', bad_login=True)
    else:
        return render_template("login.html")


@app.route("/users")
def list_users():
    users = database_data_manager.get_users()
    return render_template('user-list.html', users = users)


@app.route('/logout')
def logout():
    session.pop('username')
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run()
