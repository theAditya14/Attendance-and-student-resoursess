from flask_wtf import FlaskForm
from wtforms import StringField,IntegerField,SubmitField
from wtforms.validators import DataRequired,length

class Registration(FlaskForm):
     name = StringField("Enter student name",validators=[DataRequired()])
     student_class = StringField("Enter student class",validators=[DataRequired()])
     roll_no = IntegerField("Enter roll no",validators=[DataRequired(length(min=2))])
     submit = SubmitField("Register")



     