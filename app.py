import os
from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_pymongo import PyMongo
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from bson.objectid import ObjectId
from datetime import datetime
from dotenv import load_dotenv
import bcrypt
from forms import RegistrationForm, LoginForm, ProfileForm, CardForm
import markdown
import bleach

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['MONGO_URI'] = os.getenv('MONGO_URI')
app.config['MONGO_SSL'] = os.getenv('MONGO_SSL')
app.config['MONGO_SSL_CA_CERTS'] = os.getenv('MONGO_SSL_CA_CERTS')

mongo = PyMongo(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.name = user_data.get('name', '')
        self.email = user_data.get('email', '')
        self.phone = user_data.get('phone', '')
        self.bio = user_data.get('bio', '')
        self.birthday = user_data.get('birthday', '')
        self.country = user_data.get('country', '')
        self.city = user_data.get('city', '')


@login_manager.user_loader
def load_user(user_id):
    user_data = mongo.db.users.find_one({'_id': ObjectId(user_id)})
    if user_data:
        return User(user_data)
    return None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if mongo.db.users.find_one({'email': form.email.data}):
            flash('Email уже зарегистрирован', 'danger')
            return redirect(url_for('register'))

        hashed_password = bcrypt.hashpw(form.password.data.encode('utf-8'), bcrypt.gensalt())

        user_data = {
            'name': form.name.data,
            'email': form.email.data,
            'password': hashed_password,
            'created_at': datetime.utcnow()
        }
        mongo.db.users.insert_one(user_data)
        flash('Регистрация успешна!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_data = mongo.db.users.find_one({'email': form.email.data})
        if user_data and bcrypt.checkpw(form.password.data.encode('utf-8'), user_data['password']):
            user = User(user_data)
            login_user(user)
            return redirect(url_for('cards'))
        flash('Неверный email или пароль', 'danger')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        updates = {
            'name': form.name.data,
            'phone': form.phone.data,
            'bio': form.bio.data,
            'birthday': form.birthday.data,
            'country': form.country.data,
            'city': form.city.data
        }
        mongo.db.users.update_one(
            {'_id': ObjectId(current_user.id)},
            {'$set': updates}
        )
        flash('Профиль обновлен', 'success')
        return redirect(url_for('profile'))
    return render_template('profile.html', form=form)


@app.route('/cards')
@login_required
def cards():
    sort_by = request.args.get('sort', 'created_at')
    view = request.args.get('view', 'list')

    cards_data = list(mongo.db.cards.find({'user_id': current_user.id}).sort(sort_by, -1))

    return render_template('cards.html', cards=cards_data, view=view, sort_by=sort_by)


@app.route('/card/new', methods=['GET', 'POST'])
@login_required
def new_card():
    form = CardForm()
    if form.validate_on_submit():
        # Преобразуем Markdown в безопасный HTML
        html_content = markdown.markdown(form.content.data)
        clean_content = bleach.clean(
            html_content,
            tags=bleach.sanitizer.ALLOWED_TAGS + [
                'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                'img', 'pre', 'code', 'blockquote', 'div',
                'span', 'br', 'hr', 'strong', 'em', 'a'
            ],
            attributes={
                'img': ['src', 'alt', 'title'],
                'a': ['href', 'title'],
                'code': ['class']
            }
        )

        card_data = {
            'user_id': current_user.id,
            'title': form.title.data,
            'content': clean_content,
            'content_type': form.content_type.data,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        mongo.db.cards.insert_one(card_data)
        flash('Карточка создана', 'success')
        return redirect(url_for('cards'))
    return render_template('edit_card.html', form=form)


@app.route('/card/edit/<card_id>', methods=['GET', 'POST'])
@login_required
def edit_card(card_id):
    card = mongo.db.cards.find_one_or_404({'_id': ObjectId(card_id)})

    # Проверка владельца карточки
    if card['user_id'] != current_user.id:
        abort(403)

    form = CardForm(obj=card)

    if form.validate_on_submit():
        html_content = markdown.markdown(form.content.data)
        clean_content = bleach.clean(
            html_content,
            tags=bleach.sanitizer.ALLOWED_TAGS + [
                'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                'img', 'pre', 'code', 'blockquote', 'div',
                'span', 'br', 'hr', 'strong', 'em', 'a'
            ],
            attributes={
                'img': ['src', 'alt', 'title'],
                'a': ['href', 'title'],
                'code': ['class']
            }
        )

        updates = {
            'title': form.title.data,
            'content': clean_content,
            'content_type': form.content_type.data,
            'updated_at': datetime.utcnow()
        }
        mongo.db.cards.update_one(
            {'_id': ObjectId(card_id)},
            {'$set': updates}
        )
        flash('Карточка обновлена', 'success')
        return redirect(url_for('cards'))

    # Для редактирования показываем оригинальный Markdown
    form.content.data = card.get('original_content', card['content'])
    return render_template('edit_card.html', form=form, card=card)


@app.route('/card/delete/<card_id>', methods=['POST'])
@login_required
def delete_card(card_id):
    card = mongo.db.cards.find_one_or_404({'_id': ObjectId(card_id)})

    if card['user_id'] != current_user.id:
        abort(403)

    mongo.db.cards.delete_one({'_id': ObjectId(card_id)})
    flash('Карточка удалена', 'success')
    return redirect(url_for('cards'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)