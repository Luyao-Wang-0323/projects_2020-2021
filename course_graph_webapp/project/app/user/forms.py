# app/user/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField, TextField
from wtforms.validators import DataRequired


class SearchJobForm(FlaskForm):
    """
    Form for search a job
    """
    jobname = StringField('Job Name', validators=[DataRequired()])
    submit = SubmitField('Submit')


class UploadCVsForm(FlaskForm):
	cv = FileField('', validators=[DataRequired()])
	submit = SubmitField('Submit')
	# result = TextField('NLP Result:')

class UploadJobpostingsForm(FlaskForm):
	jobposting = FileField('', validators=[DataRequired()])
	submit = SubmitField('Submit')
	# result = TextField('NLP Result:')

