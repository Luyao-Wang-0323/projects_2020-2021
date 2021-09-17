import flask
from flask import abort, flash, redirect, render_template, url_for,request
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from firebase_admin import storage
from pyresparser import ResumeParser
from bs4 import BeautifulSoup
import nltk
import spacy
import en_core_web_sm
from spacy import displacy
import firebase_admin
from firebase_admin import credentials, initialize_app, storage, delete_app
import shutil
from random import randint
import pyrebase
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
import json
from bs4 import BeautifulSoup
import urllib
import requests
import pandas as pd
import re

from . import admin
from .. import db
from ..models import Job
from ..models import User
from ..models import Resource


def check_admin():
    """
    Prevent non-admins from accessing the page
    """
    if not current_user.is_admin:
        abort(403)

# firebase storage
def initial_firbase():
    cred = credentials.Certificate("webapp-132c7-f22a0a206a0c.json")
    initialize_app(cred, {'storageBucket': 'webapp-132c7.appspot.com'})

# upload multiple files to firebase
@admin.route('/upload', methods=['GET', 'POST'])
@login_required
def Upload_Files():
	check_admin()

	if not firebase_admin._apps:
		initial_firbase()
	list_files=list()
	if flask.request.method == "POST" :
		files = flask.request.files.getlist("file[]")
		folder=request.form.get("folder")
		for file in files:
			list_files.append(file.filename)
			file.save(str(folder)+'/' + file.filename)
			fileName = str(folder)+'/' + file.filename
			bucket = storage.bucket()
			blob = bucket.blob(fileName)
			blob.upload_from_filename(fileName)
		flash("Upload Successfully.")
	return render_template('admin/uploadfiles.html', files=list_files)
	# if flask.request.method == "POST" :

#download from firebase and update mysql
@admin.route('/update', methods=['GET', 'POST'])
@login_required
def Update_DB():
	check_admin()
	
	return render_template('admin/updateDB.html')

def list_files(bucketFolder):
    """List all files in GCP bucket."""
    bucket = storage.bucket()
    files = bucket.list_blobs(prefix=bucketFolder)
    fileList = [file.name for file in files if '.' in file.name]
    return fileList

@admin.route('/update/download', methods=['GET', 'POST'])
def admin_Download():
	global folder
	folder='download/'
	if firebase_admin._apps:
		default_app=firebase_admin.get_app(name='[DEFAULT]')
		delete_app(default_app)
	config = {
	"apiKey": "AIzaSyD0ooQ76xICk8pNAs8ws_k-CfrTXvVBu-k",
	"authDomain": "webapp-132c7.firebaseapp.com",
	"databaseURL": "https://webapp-132c7.firebaseio.com",
	"projectId": "webapp-132c7",
	"storageBucket": "webapp-132c7.appspot.com",
	"messagingSenderId": "1055448689497",
	"appId": "1:1055448689497:web:0aea66577d03a2a40b3a48",
	"measurementId": "G-HKNNPBRFEJ",
	"serviceAccount":"webapp-132c7-f22a0a206a0c.json"}
	firebase=pyrebase.initialize_app(config)
	storage = firebase.storage()
	all_files = storage.list_files()
	for file in all_files:
		# print(file.name)
		try:
			file.download_to_filename(folder + file.name)
		except:
			print('Download Failed')
	flash("Download Successfully.")
	try:
		default_app=firebase_admin.get_app(name='[DEFAULT]')
		delete_app(default_app)
	except:
		pass
	return render_template('admin/updateDB.html',folder=folder)

# extract from job posting
def extract_jp(fileName):
    with open('download/jobpostings/'+fileName,'rb') as f:
        content=f.read()
    content=content.decode('utf-8')
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(content)
    list_pos=list()
    pos_tags = [(i, i.tag_) for i in doc]
    for i in pos_tags:
        if i[1] == "NNP":
            list_pos.append(str(i[0]))
    list_ent=list()
    for ent in doc.ents:
        if ent.label_!='DATE'and ent.label_!='CARDINAL'and ent.label_!='FAC':
            list_ent.append(ent.text)
    list_word=list()
    for word in list_pos:
        if word in list_ent:
            list_word.append(word)
    require=list(set(list_word))
    list_requirements=require
    return list_requirements

def resource_link(skill):#根据skill 提取 resource link
	res_lst=[]
	url='https://www.coursera.org/search?query='+skill
	website=requests.get(url)
	soup=BeautifulSoup(website.content,'html.parser')
	tag1=soup('div')
	try:
		for tag in tag1:
			if tag.get('class',None):
				if tag.get('class',None)[0]==('tab-contents'):
					data=json.loads(tag.script.string)
					return data['itemListElement'][0]['url']
	except:
		return 'none'

def spark_clean(jsonfile):
	spark=SparkSession\
	.builder\
	.appName('job')\
	.getOrCreate()
	df=spark.read.json('jobtable.json')
	df=df.filter(~(df.requirement.isin("abc","English",'United States')))
	df=df.filter(~(df.requirement.contains('Reasonable'))) 
	df=df.filter(~(df.requirement.contains('Education'))) 
	df=df.filter(~(df.requirement.contains('Qualifications'))) 
	df=df.filter(~(df.requirement.contains('BONUS'))) 
	df=df.filter(~(df.requirement.contains('Experience')))
	df=df.filter(~(df.requirement.contains('Financial')))
	df=df.filter(~(df.requirement.contains('US')))
	df=df.filter(~(df.requirement.contains('Government')))
	df=df.filter(~(df.requirement.contains('Department')))
	df=df.filter(~(df.requirement.contains('Skills')))
	df=df.filter(~(df.requirement.contains('BS')))
	df=df.filter(~(df.requirement.contains('Degree')))
	df=df.withColumn('jobname', regexp_replace('jobname', '-', ' '))
	df=df.withColumn('requirement', regexp_replace('requirement', '-', ' '))
	df=df.withColumn('jobname', lower(col('jobname')))
	df=df.withColumn('requirement', lower(col('requirement')))
	return df

@admin.route('/update/update', methods=['GET', 'POST'])
def admin_Update():
	on=False
	global folder
	try:
		if folder:
			pass
	except:
		folder='download/'
	requirements=list()
	jobs=list()
	#for file in folder jobpostings/
	for file in os.listdir(folder+'jobpostings'):
		if file=='.DS_Store':
			continue
		else:
			require=extract_jp(file)
			jobs.append(file[:-4])
		requirements.append(require)

	jobtable=list()
	for i in range(len(jobs)):
		for j in requirements[i]:
			job=dict()
			job['jobname']=jobs[i]
			job['requirement']=j
			jobtable.append(job)
	with open('jobtable.json', 'w') as fp:
		json.dump(jobtable, fp)
	if on:
		# spark clean
		df=spark_clean('jobtable.json')

		# update jobs table
		for row in df.rdd.collect():
			jobname=row.jobname
			requirement=row.requirement
			val=(jobname,requirement)
			newjob=Job(jobname=jobname,requirement=requirement)
		# 	db.session.add(newjob)
		# db.session.commit()
			


		# update resources table
		q=Job.query.with_entities(Job.requirement).all()
		myresult = [m[0] for m in q]
		resource=list()
		list_skill=myresult
		for skill in list_skill:
			link=resource_link(skill)
			course=link.split('/')[-1].replace('-',' ')
			# val=(course,link,skill)
			newresource=Resource(course=course,link=link,knowledge=skill)
		# 	db.session.add(newresource)
		# db.session.commit()
	flash("Update Successfully.")
	return render_template('admin/updateDB.html')


@admin.route('/update/delete', methods=['GET', 'POST'])
def admin_Delete():
	global folder
	try:
		if folder:
			pass
	except:
		folder='download/'
	shutil.rmtree(folder)
	flash("Delete Successfully.")
	# cwd = os.getcwd()
	# print(cwd)
	os.mkdir(os.path.join('.','download'))
	os.mkdir(os.path.join('./download','Jobpostings'))
	os.mkdir(os.path.join('./download','CVs'))
	return render_template('admin/updateDB.html')
















