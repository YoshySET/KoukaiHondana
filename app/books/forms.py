from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired, Optional, NumberRange

class SearchBookForm(FlaskForm):
    query = StringField('タイトル、著者、ISBN等', validators=[DataRequired()])
    submit = SubmitField('検索')

class AddBookReviewForm(FlaskForm):
    rating = SelectField('評価', choices=[(str(i), '★' * i) for i in range(1, 6)], validators=[Optional()])
    review = TextAreaField('レビュー', validators=[Optional()])
    is_public = SelectField('公開設定', choices=[
        ('public', '全体公開'),
        ('friends', '友達のみ'),
        ('private', '非公開')
    ])
    submit = SubmitField('保存') 