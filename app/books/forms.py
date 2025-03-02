from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, RadioField
from wtforms.validators import DataRequired, Length, Optional

class SearchBookForm(FlaskForm):
    query = StringField('検索', validators=[DataRequired()])
    submit = SubmitField('検索')

class AddBookReviewForm(FlaskForm):
    rating = SelectField('評価', choices=[
        ('', '選択してください'),
        ('1', '★'),
        ('2', '★★'),
        ('3', '★★★'),
        ('4', '★★★★'),
        ('5', '★★★★★')
    ], validators=[Optional()])
    review = TextAreaField('レビュー', validators=[Optional(), Length(max=1000)])
    is_public = RadioField('公開設定', choices=[
        ('public', '公開'),
        ('private', '非公開')
    ], default='public')
    submit = SubmitField('保存') 