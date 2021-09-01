from typing import List, Dict
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
import util
import database_common


@database_common.connection_handler
def get_headers(cursor: RealDictCursor, table_name) -> list:
    query = """
        SELECT column_name FROM information_schema.columns
         WHERE table_name = %(user_table)s;"""
    cursor.execute(query, {"user_table": table_name})
    return cursor.fetchall()


@database_common.connection_handler
def get_questions(cursor: RealDictCursor) -> list:
    query = """
        SELECT id, title, message, vote_number, view_number, submission_time, image
        FROM question """
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_single_question(cursor: RealDictCursor, question) -> list:
    query = """
        SELECT id, title, message, vote_number, view_number, submission_time, image,
        (SELECT username FROM users WHERE id = user_id)
        FROM question WHERE id = %(question_id)s """
    cursor.execute(query, {"question_id": question})
    return cursor.fetchone()


@database_common.connection_handler
def get_latest_questions(cursor: RealDictCursor) -> list:
    query = """
        SELECT id, title, message, vote_number, view_number, submission_time, image,
        (SELECT username FROM users WHERE id = user_id)
        FROM question ORDER BY submission_time DESC LIMIT 5 """

    cursor.execute(query)

    return cursor.fetchall()


@database_common.connection_handler
def add_question(cursor: RealDictCursor, new_question) -> list:
    query = """
        INSERT INTO question (submission_time, view_number, vote_number,title, message, image, user_id)
        VALUES (%(time)s, 0, 0, %(title)s, %(message)s, %(image)s, 
        (SELECT id FROM users WHERE username = %(username)s));
        """
    cursor.execute(query,
                   {"time": util.get_current_time(), "title": new_question["title"],
                    "message": new_question["message"],
                    "image": new_question["image"], "username": new_question["username"]})


@database_common.connection_handler
def update_question(cursor: RealDictCursor, updated_question) -> None:
    query = """
        UPDATE question
        SET title = %(new_title)s , message = %(new_message)s, image = %(new_image)s
        WHERE id = %(question_id)s;
    """
    cursor.execute(query, {"new_title": updated_question["title"], "new_message": updated_question["message"],
                           "new_image": updated_question["image"], "question_id": updated_question["id"]})


@database_common.connection_handler
def remove_question(cursor: RealDictCursor, question_id) -> None:
    query = """
        DELETE FROM question_tag WHERE question_id = %(id)s;
        DELETE FROM comment USING answer
        WHERE answer.question_id = %(id)s;
        DELETE FROM answer WHERE question_id = %(id)s;
        DELETE FROM question WHERE id = %(id)s;
        """
    cursor.execute(query, {"id": question_id})


@database_common.connection_handler
def sort_questions(cursor: RealDictCursor, order_by, direction) -> list:
    query = f"""
            SELECT id, title, submission_time, message, view_number, vote_number, image,
            (SELECT username FROM users WHERE id = user_id) 
            FROM question 
            ORDER BY {order_by} {direction}; """

    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_answers(cursor: RealDictCursor, selected_question_id) -> list:
    query = """
        SELECT id, submission_time, vote_number, question_id, message, image,
        (SELECT username FROM users WHERE id = user_id) 
        FROM answer WHERE question_id = %(question_id)s;"""
    cursor.execute(query, {"question_id": selected_question_id})
    return cursor.fetchall()


@database_common.connection_handler
def add_answer(cursor: RealDictCursor, new_answer) -> None:
    if new_answer['image'] is None:
        query = """
                INSERT INTO answer (submission_time, vote_number, question_id, message, image, user_id)
                VALUES (%(time)s, 0, %(question_id)s, %(message)s, 
                (SELECT id FROM users WHERE username = %(username)s));
                """
        cursor.execute(query,
                       {"time": util.get_current_time(), "question_id": new_answer['question_id'],
                        "message": new_answer['message'], "username": new_answer["username"]})
    else:
        query = """
                INSERT INTO answer (submission_time, vote_number, question_id, message, image, user_id)
                VALUES (%(time)s, 0, %(question_id)s, %(message)s, %(image)s, 
                (SELECT id FROM users WHERE username = %(username)s));
                """
        cursor.execute(query,
                       {"time": util.get_current_time(), "question_id": new_answer['question_id'],
                        "message": new_answer['message'], "image": f"images/{new_answer['image']}",
                        "username": new_answer["username"]})


@database_common.connection_handler
def vote_answer(cursor: RealDictCursor, answer_id, value) -> None:
    if value == "Up":
        query = """ 
        UPDATE answer
        SET vote_number = vote_number + 1
        WHERE id = %(answer_id)s;
        """

        cursor.execute(query, {"answer_id": answer_id})

    elif value == "Down":
        query = """ 
                UPDATE answer
                SET vote_number = vote_number - 1
                WHERE id = %(answer_id)s;
                """

        cursor.execute(query, {"answer_id": answer_id})


@database_common.connection_handler
def get_question_id_by_answer_id(cursor: RealDictCursor, answer_id) -> list:
    query = """ 
    SELECT question_id FROM answer
    WHERE id = %(answer_id)s;"""

    cursor.execute(query, {"answer_id": answer_id})
    return cursor.fetchone()


@database_common.connection_handler
def update_answer(cursor: RealDictCursor, updated_answer) -> None:
    query = """
    UPDATE answer
    SET message = %(new_message)s, submission_time = %(time)s, image = %(image)s
    WHERE id = %(question_id)s;
    """
    cursor.execute(query, {"new_message": updated_answer["message"], "time": util.get_current_time(),
                           "question_id": updated_answer["id"], "image": updated_answer["image"]})


@database_common.connection_handler
def get_single_answer(cursor: RealDictCursor, answer) -> list:
    query = """
        SELECT id, message, vote_number, submission_time, image, question_id
        FROM answer WHERE id = %(answer_id)s """
    cursor.execute(query, {"answer_id": answer})
    return cursor.fetchone()


@database_common.connection_handler
def get_tag(cursor: RealDictCursor) -> list:
    query = """
        SELECT name
        FROM tag """
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def count_tags(cursor: RealDictCursor, tag_id) -> list:
    query = """
            SELECT tag_id
            FROM question_tag
            WHERE tag_id = %(tag)s
        """
    cursor.execute(query, {"tag": tag_id})
    return cursor.fetchall()


@database_common.connection_handler
def vote_up(cursor: RealDictCursor, element_id) -> None:
    query = """
        UPDATE question
        SET vote_number = vote_number + 1
        WHERE id = %(question_id)s"""
    cursor.execute(query, {"question_id": element_id})


@database_common.connection_handler
def vote_down(cursor: RealDictCursor, element_id) -> None:
    query = """
        UPDATE question
        SET vote_number = vote_number - 1
        WHERE id = %(question_id)s"""
    cursor.execute(query, {"question_id": element_id})


@database_common.connection_handler
def add_comment_to_question(cursor: RealDictCursor, new_comment) -> None:
    query = """
        INSERT INTO comment (question_id, answer_id, message, submission_time, edited_count, user_id)
        VALUES (%(question_id)s , null,  %(message)s, %(time)s, null,
         (SELECT id FROM users WHERE username = %(username)s));
    """
    cursor.execute(query,
                   {
                       "question_id": int(new_comment["question_id"]), "message": new_comment["message"],
                       "time": util.get_current_time(), "username": new_comment["username"]})


@database_common.connection_handler
def get_question_comment(cursor: RealDictCursor, question_id) -> list:
    query = """
        SELECT id, message, submission_time, edited_count,
        (SELECT username FROM users WHERE id = user_id)
        FROM comment
        WHERE question_id = %(question_id)s;"""
    cursor.execute(query, {"question_id": question_id})
    return cursor.fetchall()


@database_common.connection_handler
def add_tag(cursor: RealDictCursor, new_tag) -> None:
    query = """
            INSERT INTO tag (name)
            VALUES (%(new_tag)s)
            """
    cursor.execute(query,
                   {"new_tag": new_tag})


@database_common.connection_handler
def add_question_tag(cursor: RealDictCursor, question_id, tag_id) -> None:
    query = """
            INSERT INTO question_tag (question_id, tag_id)
            VALUES (%(q_id)s, %(t_id)s)
            """
    cursor.execute(query,
                   {"q_id": question_id, "t_id": tag_id})


@database_common.connection_handler
def get_id_tag(cursor: RealDictCursor, tag) -> list:
    query = """
            SELECT id
            FROM tag
            WHERE name = (%(tag)s)
            """
    cursor.execute(query,
                   {"tag": tag})
    return cursor.fetchone()


@database_common.connection_handler
def tags_for_question(cursor: RealDictCursor, question_id) -> list:
    query = """
                SELECT name, id
                FROM tag
                INNER JOIN question_tag
                ON tag.id = question_tag.tag_id
                WHERE question_id = %(question_id)s
                """
    cursor.execute(query,
                   {"question_id": question_id})
    return cursor.fetchall()


@database_common.connection_handler
def get_searched(cursor: RealDictCursor, searched_phrase) -> list:
    query = """
        SELECT DISTINCT question.id, title, question.message, question.vote_number, 
        question.view_number, question.submission_time
        FROM question LEFT JOIN answer ON question.id = answer.question_id
        WHERE LOWER(question.title) LIKE LOWER(%(searched)s) OR LOWER(question.message) LIKE LOWER(%(searched)s)
        OR LOWER(answer.message) LIKE LOWER(%(searched)s) ORDER BY submission_time;"""
    cursor.execute(query, {"searched": ("%%" + searched_phrase + "%%")})
    return cursor.fetchall()


@database_common.connection_handler
def get_searched_answers(cursor: RealDictCursor, searched_phrase) -> list:
    query = """
        SELECT DISTINCT message
        FROM answer
        WHERE LOWER(message) LIKE LOWER(%(searched)s);"""
    cursor.execute(query, {"searched": ("%%" + searched_phrase + "%%")})
    return cursor.fetchall()


@database_common.connection_handler
def get_answer_comment(cursor: RealDictCursor) -> list:
    query = """
        SELECT id, answer_id, message, submission_time, edited_count,
        (SELECT username FROM users WHERE id = user_id)
        FROM comment
        WHERE answer_id IS NOT NULL
    """
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def add_comment_to_answer(cursor: RealDictCursor, new_comment) -> None:
    query = """
        INSERT INTO comment (question_id, answer_id, message, submission_time, edited_count, user_id)
        VALUES (null , %(answer_id)s,  %(message)s, %(time)s, null,
        (SELECT id FROM users WHERE username = %(username)s));
    """
    cursor.execute(query,
                   {"answer_id": int(new_comment["answer_id"]), "message": new_comment["message"],
                    "time": util.get_current_time(), "username": new_comment["username"]})


@database_common.connection_handler
def delete_question_tag(cursor: RealDictCursor, tag_id) -> None:
    query = """
    DELETE FROM question_tag
    WHERE tag_id = %(tag_id)s;
    DELETE FROM tag
    WHERE id = %(tag_id)s;
    """
    cursor.execute(query, {'tag_id': tag_id})


@database_common.connection_handler
def get_comment(cursor: RealDictCursor, comment_id) -> list:
    query = """
        SELECT id, message, submission_time, edited_count, answer_id, question_id
        FROM comment
        WHERE id = %(comment_id)s
    """
    cursor.execute(query, {"comment_id": comment_id})
    return cursor.fetchone()


# @database_common.connection_handler
# def get_edited_count(cursor: RealDictCursor, comment_id):
#     query = """
#     SELECT edited_count
#     FROM comment
#     WHERE id = %(comment_id)s;
#     """
#     cursor.execute(query,{"comment_id": comment_id})
#     return cursor.fetchone()


@database_common.connection_handler
def update_comment(cursor: RealDictCursor, updated_comment) -> None:
    query = """
    UPDATE comment
    SET message = %(new_message)s, submission_time = %(time)s, edited_count = %(edited)s
    WHERE id = %(comment_id)s;
    """
    cursor.execute(query, {"new_message": updated_comment["message"], "time": util.get_current_time(),
                           "comment_id": updated_comment["id"], "edited": updated_comment["edited_count"]})


@database_common.connection_handler
def get_question_id_by_comment_id(cursor: RealDictCursor, comment_id) -> list:
    query = """
           SELECT question_id
           FROM comment
           WHERE id = %(comment_id)s
       """
    cursor.execute(query, {"comment_id": comment_id})
    return cursor.fetchone()


@database_common.connection_handler
def delete_comment(cursor: RealDictCursor, comment_id) -> None:
    query = """
    DELETE FROM comment
    WHERE id = %(comment_id)s;
    """
    cursor.execute(query, {'comment_id': comment_id})


@database_common.connection_handler
def check_user(cursor: RealDictCursor, user_input) -> list:
    query = """
    SELECT username FROM users WHERE username LIKE LOWER(%(user_email)s);
    """
    cursor.execute(query, {"user_email": user_input})
    return cursor.fetchone()


@database_common.connection_handler
def add_new_user(cursor: RealDictCursor, user_email, user_password) -> None:
    query = """
    INSERT INTO users (username, password_digest)
    VALUES (%(user_email)s, %(hashed_password)s);
    """
    cursor.execute(query, {"user_email": user_email, "hashed_password": user_password})


@database_common.connection_handler
def get_user(cursor: RealDictCursor, user_id) -> list:
    query = """
    SELECT username FROM users WHERE id = %(id)s;
    """
    cursor.execute(query, {"id": user_id})
    return cursor.fetchone()


@database_common.connection_handler
def delete_answer(cursor: RealDictCursor, answer_id) -> None:
    query = """
        DELETE FROM comment
        WHERE answer_id = %(answer_id)s;
        DELETE FROM answer
        WHERE id = %(answer_id)s;
        """
    cursor.execute(query, {'answer_id': answer_id})


@database_common.connection_handler
def get_answer_id_by_comment_id(cursor: RealDictCursor, comment_id) -> list:
    query = """
    SELECT answer_id
    FROM comment
    WHERE id = %(comment_id)s;
    """
    cursor.execute(query, {"comment_id": comment_id})
    return cursor.fetchone()


@database_common.connection_handler
def get_password(cursor: RealDictCursor, email) -> list:
    query = """
    SELECT password_digest FROM users 
    WHERE username = %(username)s;
    """
    cursor.execute(query, {"username": email})
    return cursor.fetchone()


@database_common.connection_handler
def get_users(cursor: RealDictCursor) -> list:
    query = """
    SELECT username, registration_date
    FROM users;"""
    cursor.execute(query)
    return cursor.fetchall()