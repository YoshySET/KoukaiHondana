from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Email, ValidationError
from app.models import User
from flask_login import current_user

class EditProfileForm(FlaskForm):
    username = StringField('ユーザー名', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('メールアドレス', validators=[DataRequired(), Email()])
    about_me = TextAreaField('自己紹介', validators=[Length(max=140)])
    privacy_setting = SelectField('プライバシー設定', choices=[
        ('public', '全体公開'),
        ('friends', '友達のみ'),
        ('private', '非公開')
    ])
    submit = SubmitField('保存')
    
    def __init__(self, original_username, original_email, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email
        
    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError('このユーザー名は既に使用されています。')
                
    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user is not None:
                raise ValidationError('このメールアドレスは既に登録されています。') 