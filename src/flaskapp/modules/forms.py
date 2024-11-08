from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, HiddenField, FormField, Form, FieldList, Field
from wtforms.widgets import TextInput, SubmitInput
from wtforms.validators import DataRequired, EqualTo, Email, ValidationError, Length
from flaskapp.main import ar
from database.main import qr

class LoginForm(FlaskForm):
    username = StringField(ar.username + ":", validators=[DataRequired(), Length(max=32)])
    password = PasswordField(ar.password + ":", validators=[DataRequired(), Length(max=32)])
    remember_me = BooleanField(ar.remember_me)
    submit = SubmitField(ar.login)

class RegisterForm(FlaskForm):
    username = StringField(ar.username + ":", validators=[DataRequired(), Length(max=32)])
    email = StringField(ar.email + ":", validators=[DataRequired(), Email(), Length(max=64)])
    password = PasswordField(ar.password + ":", validators=[DataRequired(), Length(max=32)])
    password2 = PasswordField("أعد " + ar.password + ":", validators=[DataRequired(), EqualTo("password"), Length(max=32)])
    remember_me = BooleanField(ar.remember_me)
    submit = SubmitField(ar.register)

    def validate_username(self, username):
        if qr.doesValueExist(table='users', column='username', value=username.data):
            raise ValidationError(ar.username +  'هذا سبق استعماله, اختر غيره')
            
        
    def validate_email(self, email):
        if qr.doesValueExist(table='users', column='email', value=email.data):
            raise ValidationError('هذا سبق استعماله, اختر غيره أو سجّل دخولك به')

class ContextForm(Form):
    trcontext = StringField('السياق العرنجي', render_kw={"placeholder": "مثال: كن إيجابي!"}, validators=[Length(max=64)])
    arcontext = StringField('السياق الصحيح', render_kw={"placeholder": "مثال: تفاءل!"}, validators=[Length(max=64)])

    def validate_trcontext(self, trcontext):
        self.validate_context(trcontext.data, self.arcontext.data)

    def validate_arcontext(self, arcontext):
        self.validate_context(arcontext.data, self.trcontext.data)

    def validate_context(self, c1, c2):
        if not c1 and c2:
            raise ValidationError("لا يجوز أن تملأ أحد الفراغين دون صاحبه")




class AddEntry(FlaskForm):
    original = StringField('اللفظة الأعجمية مكتوبة بلغتها:', render_kw={"placeholder": "مثال: Negatives"}, validators=[DataRequired(), Length(max=32)])
    translationese = StringField('اللفظة العرنجية مكتوبة بالعربية:', render_kw={"placeholder": "مثال: سلبيات"}, validators=[DataRequired(), Length(max=32)])
    origin = SelectField('دخيل من', validators=[DataRequired()], choices=list(ar.languages.items()))
    corrections = StringField('المعنى المراد (اختياري), افصل بين المعاني بفواصل:', render_kw={"placeholder": "مثال: مساوئ, عيوب"}, validators=[Length(max=256)])
    context = FormField(ContextForm, "سياق ورود المعنى (اختياري):")

    submit = SubmitField("أضف")
