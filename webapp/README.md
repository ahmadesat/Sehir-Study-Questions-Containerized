# Sehir-Study-Questions

Website similar to Kaggle made for my University using Python and MySQL

## How To Use :

For MySQL:

1. Open MySQL and make a schema with the name "studyquestions"
2. Open the SQL file "studyquestions_courses" and execute it
3. Open the SQL file "allTables" and execute it.

For Python:

3. Make sure you change the host,user, and password parameters in here, to whatever you put in your MySQL Database
```python
database = mysql.connector.connect(host="localhost",
                                   user="userHere",
                                   password="passwordHere",
                                   database="studyquestions")
 ```


5. Run main.py
6. Navigate to http://127.0.0.1:5000 and enjoy the website :)

## For Testing :
To test the website **as an Instructor**, simply register an account with the following credentials:

Name : Testing Instructor

email : testing@sehir.edu.tr

password : *any password*

Then search for a course named **Testing Purposes**
You will be the instructor of that course.


To test the website **as a Student**, credentials can be anything you'd like
but make sure you **use the domain *@std.sehir.edu.tr* in the email section**
