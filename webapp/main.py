from datetime import date

import mysql.connector
from flask import Flask, request, redirect, url_for, session
from flask import render_template


app = Flask(__name__)

app.secret_key = "WHATEVERYOUWANT"
database = mysql.connector.connect(host="mysql", port='3306',
								   user="root",
								   password="mysqlsehir",
								   database="studyquestions")

cursor = database.cursor(buffered=True)


@app.route('/', methods=["POST", "GET"])
def searchfor():
    cursor.execute("select course_code from courses")
    all_courses = cursor.fetchall()
    listOfCourses = []
    for course in all_courses:
        listOfCourses.append(course[0])
    if request.method == "GET":

        if 'loggedin' in session:
            # User is loggedin show them the home page
            return render_template('main.html', courses=listOfCourses, name=session['name'])

        else:
            return redirect(url_for('login'))

    else:
        searchquery = request.form["searchbar"]
        cursor.execute("select course_name from courses WHERE courses.course_code = %s", (searchquery,))
        course_name = cursor.fetchall()
        return redirect("/{name_of_course}".format(name_of_course=course_name[0][0]))


@app.route('/aboutUs')
def aboutUs():
    return render_template('aboutUs.html')


@app.route("/<name_of_course>", methods=["POST", "GET"])
def course_page(name_of_course):
    if 'loggedin' in session:
        # Fetch the coursename
        if request.method == "GET":
            # Fetch the questions for this course
            cursor.execute(
                "select question.id, description, difficulty, p_value, postingDate from question,courses WHERE courses.course_name = %s and question.course_id = courses.id ",
                (name_of_course,))
            questions = cursor.fetchall()

            id = []
            desc = []
            difficulty = []
            p_value = []
            dates = []
            for question in questions:
                id.append(question[0])
                desc.append(question[1])
                difficulty.append(question[2])
                p_value.append(question[3])
                dates.append(question[4].strftime("%d/%m/%Y"))

            # Check whether it is a Staff Member or not

            cursor.execute('SELECT * FROM courses WHERE courses.course_name = %s and courses.course_prof = %s',
                           (name_of_course, session['name'],))
            checkIfThisIsProf = cursor.fetchone()

            if checkIfThisIsProf:
                return render_template('course_page_staff.html', name=session['name'], coursename=name_of_course,
                                       q_id=id, desc=desc, difficulty=difficulty, p_value=p_value, dates=dates)




            else:
                return render_template('course_page.html', name=session['name'], coursename=name_of_course, q_id=id,
                                       desc=desc, difficulty=difficulty, p_value=p_value, dates=dates)

        else:
            if request.form["btn"] == "Post A Question":
                return redirect("/{name_of_course}/post".format(name_of_course=name_of_course))

    return redirect(url_for('login'))


@app.route("/<name_of_course>/post", methods=["POST", "GET"])
def postQuestion(name_of_course):
    if 'loggedin' in session:

        cursor.execute('SELECT * FROM courses WHERE courses.course_name = %s and courses.course_prof = %s',
                       (name_of_course, session['name'],))
        checkIfThisIsProf = cursor.fetchone()

        if checkIfThisIsProf:

            if request.method == "GET":
                return render_template('postquestion.html', name=session['name'])

            else:
                description = request.form["description"]
                difficulty = request.form["difficulty"]
                p_value = request.form["p_value"]
                currentDate = date.today()

                cursor.execute(
                    "insert into question(course_id,posted_by,description, input, output, difficulty, p_value, postingDate)"
                    "values (%s,%s,%s,%s,%s,%s,%s,%s)",
                    (checkIfThisIsProf[0], session['id'], description, 123, 321, difficulty, p_value, currentDate))

                database.commit()

                return redirect("/{name_of_course}".format(name_of_course=name_of_course))
        else:
            return redirect("/{name_of_course}".format(name_of_course=name_of_course))



    else:
        return redirect(url_for('login'))


@app.route("/<name_of_course>/<question_id>", methods=["POST", "GET"])
def viewQuestion(name_of_course, question_id):
    if 'loggedin' in session:

        cursor.execute(
            "select description from question WHERE question.id=%s",
            (question_id,))
        question = cursor.fetchall()
        desc = question[0]

        cursor.execute("SELECT rate FROM rated_by WHERE question_id=%s", (question_id,))
        rates = cursor.fetchall()

        ratings = []
        for rate in rates:
            ratings.append(rate[0])

        if len(ratings) == 0:
            rating = 0
        else:
            rating = sum(ratings) / len(ratings)

        cursor.execute('SELECT * FROM courses WHERE courses.course_name = %s and courses.course_prof = %s',
                       (name_of_course, session['name'],))
        checkIfThisIsProf = cursor.fetchone()

        if checkIfThisIsProf:

            if request.method == "GET":
                return render_template('viewQuestion_staff.html', name=session['name'], desc=desc[0], rating=rating)

            else:
                cursor.execute("DELETE FROM question WHERE id=%s", (question_id,))
                database.commit()
                return redirect(url_for("course_page", name_of_course=name_of_course))

        else:
            if request.method == "GET":
                return render_template('viewQuestion.html', name=session['name'], desc=desc[0], rating=rating)

            else:
                cursor.execute("select * from rated_by WHERE student_id=%s and question_id=%s",
                               (session['id'], question_id,))
                ratingExists = cursor.fetchall()

                if ratingExists:
                    errorMsg = "You Have Already Rated This Question Before"
                    return render_template('viewQuestion.html', name=session['name'], desc=desc[0], rating=rating,
                                           errorMsg=errorMsg)
                else:
                    rateToGive = int(request.form["rateToGive"])
                    cursor.execute("insert into rated_by(rate,student_id, question_id)"
                                   "values (%s,%s,%s)",
                                   (rateToGive, session['id'], question_id))

                    database.commit()

                    return redirect(url_for("course_page", name_of_course=name_of_course))



    else:
        return redirect(url_for('login'))


@app.route("/<name_of_course>/<question_id>/answers", methods=["POST", "GET"])
def viewAllAnswers(name_of_course, question_id):
    if 'loggedin' in session:

        if request.method == "GET":
            cursor.execute(
                "select  answer.description, student.name, status, answer.postingDate,student.score from answer,student WHERE answer.posted_by=student.id and answer.q_id = %s",
                (question_id,))
            answers = cursor.fetchall()

            desc = []
            posted_by = []
            status = []
            dates = []
            scores = []
            for answer in answers:
                desc.append(answer[0])
                posted_by.append(answer[1])
                status.append(answer[2])
                dates.append(answer[3].strftime("%d/%m/%Y"))
                scores.append(answer[4])

            cursor.execute('SELECT * FROM courses WHERE courses.course_name = %s and courses.course_prof = %s',
                           (name_of_course, session['name'],))
            checkIfThisIsProf = cursor.fetchone()

            if checkIfThisIsProf:
                return render_template('viewallanswers_staff.html', name=session['name'], desc=desc,
                                       posted_by=posted_by, correctOrNot=status, dates=dates, score=scores)
            else:
                return render_template('viewallanswers.html', name=session['name'], desc=desc, posted_by=posted_by,
                                       correctOrNot=status, dates=dates, score=scores)



    else:
        return redirect(url_for('login'))


@app.route("/<name_of_course>/<question_id>/answers/<poster_name>", methods=["POST", "GET"])
def viewAnswer(name_of_course, question_id, poster_name):
    if 'loggedin' in session:

        cursor.execute(
            "select answer.description, student.name, status, student.id from answer,question,student WHERE question.id=%s and student.name = %s and answer.posted_by=student.id and answer.q_id = question.id",
            (question_id, poster_name))
        answers = cursor.fetchall()
        desc = []
        posted_by = []
        status = []
        id_is = []
        for answer in answers:
            desc.append(answer[0])
            posted_by.append(answer[1])
            status.append(answer[2])
            id_is.append(answer[3])

        if request.method == "GET":

            cursor.execute('SELECT * FROM courses WHERE courses.course_name = %s and courses.course_prof = %s',
                           (name_of_course, session['name'],))
            checkIfThisIsProf = cursor.fetchone()

            if checkIfThisIsProf:

                return render_template('viewAnswer_staff.html', name=session['name'], desc=desc[0],
                                       posted_by=posted_by[0],
                                       correctOrNot=status[0])

            else:
                return render_template('viewAnswer.html', name=session['name'], desc=desc[0],
                                       posted_by=posted_by[0], )

        else:
            cursor.execute("select status from answer WHERE q_id=%s and posted_by=%s",
                           (question_id, id_is[0]))
            statusExists = cursor.fetchall()

            if statusExists[0][0] != -1:
                errorMsg = "You Have Already Graded This Solution Before"
                return render_template('viewAnswer_staff.html', name=session['name'], desc=desc[0],
                                       posted_by=posted_by[0],
                                       correctOrNot=status[0], errorMsg=errorMsg)
            else:
                gradeToGive = int(request.form["gradeToGive"])
                cursor.execute("UPDATE answer,student SET status= %s WHERE answer.q_id=%s  and answer.posted_by=%s",
                               (gradeToGive, question_id, id_is[0]))
                cursor.execute("SELECT status FROM answer WHERE answer.q_id=%s and  answer.posted_by=%s",
                               (question_id, id_is[0],))

                currentStatus = cursor.fetchall()[0][0]

                if currentStatus == 1:
                    cursor.execute(
                        "select score,p_value FROM student,question WHERE student.name=%s and question.id=%s",
                        (posted_by[0], question_id))
                    scoreAndValue = cursor.fetchall()

                    thescore = []
                    for sv in scoreAndValue:
                        thescore.append(sv[0] + sv[1])

                    cursor.execute("UPDATE student SET score= %s WHERE name=%s", (thescore[0], posted_by[0],))

                database.commit()

                return redirect(url_for("viewAllAnswers", name_of_course=name_of_course, question_id=question_id))



    else:
        return redirect(url_for('login'))


@app.route("/<name_of_course>/<question_id>/answer", methods=["POST", "GET"])
def postAnswer(name_of_course, question_id):
    if 'loggedin' in session:
        errorMsg = ""
        if request.method == "GET":
            return render_template("postanswer.html", name=session['name'])

        else:
            description = request.form["description"]
            currentDate = date.today()

            cursor.execute("select * from answer WHERE answer.posted_by=%s and answer.q_id=%s",
                           (session['id'], question_id))
            answerExists = cursor.fetchall()

            if answerExists:
                errorMsg = "You Have Already Answered This Question Before"
                return render_template("postanswer.html", name=session['name'], errorMsg=errorMsg)

            else:
                cursor.execute("insert into answer(posted_by,q_id, description,postingDate)"
                               "values (%s,%s,%s,%s)",
                               (session['id'], question_id, description, currentDate))

                database.commit()

                return redirect("/{name_of_course}".format(name=session['name'], name_of_course=name_of_course))



    else:
        return redirect(url_for('login'))


@app.route('/myprofile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:

        domain = session['email'].split('@')[1]

        if domain == 'sehir.edu.tr':
            # We need all the account info for the user so we can display it on the profile page
            cursor.execute('SELECT * FROM instructor WHERE id = %s', (session['id'],))
            account = cursor.fetchone()

            # Show the profile page with account info
            return render_template('profile.html', name=account[1], email=account[2])


        elif domain == 'std.sehir.edu.tr':
            # We need all the account info for the user so we can display it on the profile page
            cursor.execute('SELECT * FROM student WHERE id = %s', (session['id'],))
            account = cursor.fetchone()

            # Show the profile page with account info
            return render_template('studentprofile.html', name=account[1], email=account[2], score=account[4])

    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


""" Account Handling"""


@app.route('/register', methods=["POST", "GET"])
def register():
    if 'loggedin' in session:
        return redirect("/")

    msg = ''
    if request.method == "GET":
        return render_template('register.html')



    else:
        user_name = request.form["user_name"]
        user_email = request.form["user_email"]
        user_password = request.form["user_password"]
        domain = user_email.split('@')[1]

        check = True

        if not user_email or not user_password or not user_name:
            msg = 'Missing Required Fields'
            check = False


        elif domain != "sehir.edu.tr" and domain != "std.sehir.edu.tr":
            msg = "You can NOT access this website with this email"
            check = False

        if domain == "sehir.edu.tr":
            cursor.execute("select * from instructor")
            all_users = cursor.fetchall()

            for user in all_users:
                if user[2].lower() == user_email.lower() or user[1].lower == user_name.lower():
                    msg = "This user already exists"
                    check = False


        elif domain == "std.sehir.edu.tr":
            cursor.execute("select * from student")
            all_users = cursor.fetchall()

            for user in all_users:
                if user[2].lower() == user_email.lower() or user[1].lower == user_name.lower():
                    msg = "This user already exists"
                    check = False

        if check == True:

            if domain == "sehir.edu.tr":
                cursor.execute("insert into instructor(name,email,password)"
                               "values (%s,%s,%s)", (user_name, user_email, user_password))


            elif domain == "std.sehir.edu.tr":
                cursor.execute("insert into student(name,email,password)"
                               "values (%s,%s,%s)", (user_name, user_email, user_password))

            database.commit()
            return redirect("/login")

        else:
            return render_template('register.html', msg=msg)


@app.route('/login', methods=["POST", "GET"])
def login():
    if 'loggedin' in session:
        return redirect("/")

    if request.method == "GET":
        return render_template("login.html")

    else:

        user_email = request.form["user_email"]
        user_password = request.form["user_password"]

        domain = user_email.split('@')[1]

        if domain == "sehir.edu.tr":
            cursor.execute("select * from instructor WHERE email = %s AND password = %s",
                           (user_email, user_password,))
            account = cursor.fetchone()
            if account:
                session['loggedin'] = True
                session['id'] = account[0]
                session['name'] = account[1]
                session['email'] = account[2]
                # Redirect to home page
                print("Login Successful !")
                print(session['email'])
                return redirect("/")

            else:
                msg = 'Incorrect Email or Password'
                return render_template("login.html", msg=msg)

        elif domain == "std.sehir.edu.tr":
            cursor.execute("select * from student WHERE email = %s AND password = %s",
                           (user_email, user_password,))
            account = cursor.fetchone()

            if account:
                session['loggedin'] = True
                session['id'] = account[0]
                session['name'] = account[1]
                session['email'] = account[2]
                # Redirect to home page
                print("Login Successful !")
                print(session['email'])
                return redirect("/")

            else:
                msg = 'Incorrect Email or Password'
                return render_template("login.html", msg=msg)

        else:
            msg = 'Incorrect Email or Password'
            return render_template("login.html", msg=msg)


@app.route('/pythonlogin/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('email', None)
    # Redirect to login page
    return redirect("/login")


if __name__ == '__main__':
    app.run()
