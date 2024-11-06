from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, HiddenField
from wtforms.validators import DataRequired, EqualTo, Email, ValidationError, Length
from flaskapp.main import ar
from database.main import qr
class LoginForm(FlaskForm):
    username = StringField(ar.username, validators=[DataRequired()])
    password = PasswordField(ar.password, validators=[DataRequired()])
    remember_me = BooleanField(ar.remember_me)
    submit = SubmitField(ar.login)

class RegisterForm(FlaskForm):
    username = StringField(ar.username, validators=[DataRequired()])
    email = StringField(ar.email, validators=[DataRequired(), Email()])
    password = PasswordField(ar.password, validators=[DataRequired()])
    password2 = PasswordField("أعد " + ar.password, validators=[DataRequired(), EqualTo("password")])
    remember_me = BooleanField(ar.remember_me)
    submit = SubmitField(ar.register)

    def validate_username(self, username):
        if qr.doesValueExist(table='users', column='username', value=username.data):
            raise ValidationError(ar.username +  'هذا سبق استعماله, اختر غيره')
            
        
    def validate_email(self, email):
        if qr.doesValueExist(table='users', column='email', value=email.data):
            raise ValidationError('هذا سبق استعماله, اختر غيره أو سجّل دخولك به')


class AddEntry(FlaskForm):
    original = StringField('اللفظة الأعجمية مكتوبة بلغتها', render_kw={"placeholder": "مثال: Negatives"}, validators=[DataRequired(), Length(max=32)])
    translationese = StringField('اللفظة العرنجية مكتوبة بالعربية', render_kw={"placeholder": "مثال: سلبيات"}, validators=[DataRequired(), Length(max=32)])
    origin = SelectField('دخيل من', validators=[DataRequired()], choices=list(ar.languages.items()))
    corrections = TextAreaField('المعنى المراد (اختياري), افصل بين المعاني بفواصل', render_kw={"placeholder": "مثال: مساوئ, عيوب"}, validators=[Length(max=256)])

    submit = SubmitField("أضف")
