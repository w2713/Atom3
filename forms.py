from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, DateField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional

class RegistrationForm(FlaskForm):
    name = StringField('ФИО', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Подтвердите пароль',
                                    validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')

class ProfileForm(FlaskForm):
    name = StringField('ФИО', validators=[DataRequired()])
    email = StringField('Email', render_kw={'readonly': True})
    phone = StringField('Телефон', validators=[Optional()])
    bio = TextAreaField('О себе', validators=[Optional()])
    birthday = DateField('День рождения', format='%Y-%m-%d', validators=[Optional()])
    country = StringField('Страна', validators=[Optional()])
    city = StringField('Город', validators=[Optional()])
    submit = SubmitField('Обновить профиль')

class CardForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField('Содержимое', validators=[DataRequired()], render_kw={"rows": 10})
    content_type = SelectField('Тип контента', choices=[
        ('text', 'Текст'),
        ('code', 'Код'),
        ('image', 'Изображение'),
        ('video', 'Видео'),
        ('audio', 'Аудио'),
        ('link', 'Ссылка'),
        ('document', 'Документ'),
        ('quote', 'Цитата')
    ], default='text')
    submit = SubmitField('Сохранить')