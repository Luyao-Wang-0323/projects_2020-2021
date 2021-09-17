# demo
knowledge graph web app


# install flask and vitual enviroment:
https://scotch.io/tutorials/getting-started-with-flask-a-python-microframework

main references:
https://www.digitalocean.com/community/tutorials/build-a-crud-web-app-with-python-and-flask-part-one

https://medium.com/@abdelhedihlel/upload-files-to-firebase-storage-using-python-782213060064

if there is a warning : "WARNING: This is a development server. Do not use it in a production deployment."
export FLASK_ENV=development

virtualenv env

source env/bin/activate

other reference:
https://hackersandslackers.com/manage-files-in-google-cloud-storage-with-python/

https://www.digitalocean.com/community/tutorials/how-to-make-a-web-application-using-flask-in-python-3#prerequisites


# web:http://127.0.0.1:5000/

home:

index: function:{register,login}

if login successfully:

  user dashboard: function:{serch, recommand(personalization), upload files(to firebase)} 
  
or

  admin user dashboard: function:{upload a lot of/single files to firebase, delete files from firebase, analize, update mysql}
 
# user and admin
user: forms.py, views.py

admin: forms.py, views.py

forms.py: create class, including attributes and methods.

views.py: initialize an object of the class and use its methods, connect database and commit the request, return a html template.

