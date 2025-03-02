from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Email, ValidationError
from app.models import User

class EditProfileForm(FlaskForm):
    username = StringField('ユーザー名', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('メールアドレス', validators=[DataRequired(), Email()])
    about_me = TextAreaField('自己紹介', validators=[Length(max=500)])
    submit = SubmitField('更新')
    
    def __init__(self, original_username, original_email, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email
    
    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError('このユーザー名は既に使用されています。別のユーザー名を選んでください。')
    
    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user is not None:
                raise ValidationError('このメールアドレスは既に使用されています。別のメールアドレスを入力してください。') 