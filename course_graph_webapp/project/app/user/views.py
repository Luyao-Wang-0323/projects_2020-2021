# app/user/views.py
import flask
from flask import abort, flash, redirect, render_template, url_for
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
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("TkAgg")

from . import user
from .forms import SearchJobForm, UploadCVsForm, UploadJobpostingsForm
from .. import db
from ..models import Job
from ..models import User
from ..models import Resource
from ..models import Knowledge


# Job Search Views

@user.route('/search', methods=['GET', 'POST'])
@login_required
def Search_jobs():
    """
    List all requirements
    """
    form=SearchJobForm()
    if form.validate_on_submit():
        jobname=form.jobname.data
        # q=Job.query.with_entities(Job.jobname, Job.requirement).filter_by(jobname=jobname).all()
        search = "%{}%".format(jobname)
        q=db.session.query(Job,Resource).filter(Job.requirement==Resource.knowledge).with_entities(Job.jobname, Job.requirement,Resource.course,Resource.link).filter(Job.jobname.like(search)).all()
        # print(q)
        if q is None:
            flash("can't find this job in database.")
            return render_template('user/search/search.html',
                           form=form,title="Search Job")
        else:
            requirements=q
        return render_template('user/search/jobs.html',
                           requirements=requirements, title="Jobs")
    return render_template('user/search/search.html',
                           form=form,title="Search Job")

# firebase storage
def initial_firbase():
    cred = credentials.Certificate("webapp-132c7-f22a0a206a0c.json")
    initialize_app(cred, {'storageBucket': 'webapp-132c7.appspot.com'})

# upload Views

@user.route('/upload', methods=['GET','POST'])
@login_required
def Upload():

    return render_template('user/upload/upload.html')

# extract from cv
existingskills=''
def extract_cv(fileName):
    nltk.download('stopwords')
    data1 = ResumeParser(fileName).get_extracted_data()
    skills = data1['skills']
    skills_str = str(skills)
    skills_str = skills_str.replace('[','')
    skills_str = skills_str.replace(']','')
    skills_str = skills_str.replace("'",'')
    skills_str = skills_str.replace("'",'')
    existingskills=skills_str
    return existingskills

# extract from job posting
list_requirements=list()
def extract_jp(fileName):
    with open(fileName,'rb') as f:
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



@user.route('/upload/cv', methods=['GET','POST'])
@login_required
def Upload_cvs():
    if not firebase_admin._apps:
        initial_firbase()
    form=UploadCVsForm()
    if form.validate_on_submit():
        # save local
        filename = secure_filename(form.cv.data.filename)
        form.cv.data.save('CVs/' + filename)
        # save in firebase
        fileName = 'CVs/' + filename
        bucket = storage.bucket()
        blob = bucket.blob(fileName)
        blob.upload_from_filename(fileName)
        flash("Upload CV Successfully.")
        # extract info
        global existingskills
        existingskills=extract_cv(fileName)
        #update user
        current_user.existingskills=existingskills
        db.session.commit()

    return render_template('user/upload/cv.html', existingskills=existingskills, form=form)
    
    

@user.route('/upload/jobposting', methods=['GET','POST'])
@login_required
def Upload_jobpostings():
    if not firebase_admin._apps:
        initial_firbase()
    form=UploadJobpostingsForm()
    if form.validate_on_submit():
        filename = secure_filename(form.jobposting.data.filename)
        form.jobposting.data.save('Jobpostings/' + filename)
        fileName = 'Jobpostings/' + filename
        bucket = storage.bucket()
        blob = bucket.blob(fileName)
        blob.upload_from_filename(fileName)
        flash("Upload jobposting Successfully.")
        global list_requirements
        list_requirements=extract_jp(fileName)
        # form.result.data=list_requirements
    return render_template('user/upload/jobposting.html', list_requirements=list_requirements, form=form)

    
# recommand view
def seperate_forest(list_tuples):
    a=list_tuples
    forest=list()
    change=False
    tree=list()
    while a:
        if change==True:
            change=False
            length=len(a)
            delete=list()
            for i in range(length):
                if a[i][0] in node:
                    change=True
                    tree.append(a[i])
                    if a[i][1] not in node:
                        node.append(a[i][1])
                    delete.append(a[i])
                else:
                    if a[i][1] in node:
                        change=True
                        tree.append(a[i])
                        node.append(a[i][0])
                        delete.append(a[i])
            for d in delete:
                a.remove(d)
        else:
            if tree:
                forest.append(tree)
                tree=list()
            tree.append(a[0])
            node=list(set(a[0]))
            a.remove(a[0])
            change=True
            length=len(a)
            delete=list()
            for i in range(length):
                if a[i][0] in node:
                    change=True
                    tree.append(a[i])
                    if a[i][1] not in node:
                        node.append(a[i][1])
                    delete.append(a[i])
                else:
                    if a[i][1] in node:
                        change=True
                        tree.append(a[i])
                        node.append(a[i][0])
                        delete.append(a[i])
            for d in delete:
                a.remove(d)
    forest.append(tree)
    list_forest=forest
    return list_forest

def draw_graphs(list_forest):
    picnames=list()
    val_map=dict()
    i=1
    for f in list_forest:
        for j in f:
            if j[0]==j[1]:
                val_map[j[0]]=1.0
        graph = nx.DiGraph()
        graph.add_edges_from(f)
        values = [val_map.get(node, 0.45) for node in graph.nodes()]

        pos=nx.spring_layout(graph)
        nx.draw(graph, pos,ax=plt.figure().add_subplot(111),node_color = values,with_labels=True,node_size=2000,font_size=10,font_color='white')
    #     plt.show()
        plt.savefig('app/static/photo/testplot'+str(i)+'.png')
        picnames.append('photo/testplot'+str(i)+'.png')
        plt.clf()
        i+=1
    # print(picnames)    
    return picnames


@user.route('/recommand', methods=['GET','POST'])
@login_required
def Recommand():
    global list_requirements
    global existingskills
    picnames=list()
    rs=list(set(list_requirements)-set(existingskills))
    if flask.request.method == "POST":
        list_tuples=list()
        topics=list()
        for r in rs:
        #   get topic and prereq from knowledge where r in skills
            search="%{}%".format(r.lower())
            q=Knowledge.query.with_entities(Knowledge.topic, Knowledge.prereq).filter(Knowledge.skills.like(search)).all()
            # prereqs=[i[1] for i in q]
            topics.extend([a[0] for a in q])
            for i in q:
                topic=i[0]
                if i[1] is not None:
                    prereq=i[1].split(',')
                    for j in prereq:
                        list_tuples.append((topic,j))
        list_child=[i[1] for i in list_tuples]
        topics=list(set(topics))
        for t in topics:
            if t in list_child: 
                pass
            else: 
                list_tuples.append((t,t))
                topics
        # print(list_tuples)
        list_forest=seperate_forest(list_tuples)
        picnames.extend(draw_graphs(list_forest))
        # print(picnames)
    # show all picture in picnames on html
    return render_template('user/recommand/recommand.html', existingskills=existingskills, list_requirements=list_requirements,picnames=picnames)
