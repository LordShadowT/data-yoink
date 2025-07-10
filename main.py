from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectMultipleField, RadioField, validators
from wtforms.widgets import CheckboxInput, ListWidget
from urllib.request import urlopen
import json
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secure_secret_key_here'


# Custom widget for checkbox list
class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

def get_location_from_ip(ip: str):
    return json.load(urlopen(f'https://ipinfo.io/{ip}/json'))


# Survey form
class SurveyForm(FlaskForm):
    age = IntegerField(
        "Ihr Alter:",
        validators=[
            validators.InputRequired(message="Dieses Feld ist erforderlich"),
            validators.NumberRange(min=16, max=120,
                                   message="Bitte geben Sie ein gültiges Alter zwischen 16 und 120 ein")
        ],
        render_kw={"class": "form-control", "placeholder": "Alter in Jahren"}
    )

    social_media = MultiCheckboxField(
        "Welche Social-Media Plattformen nutzen Sie regelmäßig?",
        choices=[
            ('facebook', 'Facebook'),
            ('instagram', 'Instagram'),
            ('tiktok', 'TikTok'),
            ('twitter', 'Twitter/X'),
            ('linkedin', 'LinkedIn'),
            ('whatsapp', 'WhatsApp'),
            ('snapchat', 'Snapchat'),
            ('youtube', 'YouTube'),
            ('reddit', 'Reddit'),
            ('pinterest', 'Pinterest'),
            ('discord', 'Discord'),
            ('none', 'Keine der genannten'),
            ('other', 'Andere Plattformen')
        ],
        validators=[validators.InputRequired(message="Bitte wählen Sie mindestens eine Option")],
    )

    password_manager = RadioField(
        "Verwenden Sie einen Passwort-Manager?",
        choices=[
            ('yes', 'Ja, regelmäßig'),
            ('sometimes', 'Manchmal'),
            ('no', 'Nein, nie'),
            ('dont_know', 'Ich weiß nicht, was das ist')
        ],
        validators=[validators.InputRequired(message="Bitte wählen Sie eine Option")],
        default='no'
    )

    hacked_before = RadioField(
        "Wurden Ihre Online-Konten schon einmal kompromittiert?",
        choices=[
            ('yes', 'Ja, mindestens einmal'),
            ('suspected', 'Ich vermute es'),
            ('no', 'Nein, nie'),
            ('dont_know', 'Ich weiß es nicht')
        ],
        validators=[validators.InputRequired(message="Bitte wählen Sie eine Option")],
        default='no'
    )

    email = StringField(
        "E-Mail Adresse (für Rückfragen o.ä.):",
        validators=[
            validators.InputRequired(message="Dieses Feld ist erforderlich"),
            validators.Email(message="Bitte geben Sie eine gültige E-Mail Adresse ein"),
            validators.Length(max=100, message="E-Mail Adresse ist zu lang")
        ],
        render_kw={"class": "form-control", "placeholder": "beispiel@email.de"}
    )


# Routes
@app.route('/958662524-206774217', methods=['GET', 'POST'])
def survey():
    form = SurveyForm()
    user_data = ([{
        'time': str(datetime.now()),
        'host': request.headers['Host'],
        'user_agent': request.headers.get('User-Agent', 'Unknown'),
        'language': request.headers.get('Accept-Language', 'en-US'),
        'ip_address': request.remote_addr,
        'location': get_location_from_ip(request.remote_addr),
        'session_id': request.cookies.get('session', 'Unknown')
    }])
    if form.validate_on_submit():
        if os.path.exists('survey_data.json'):
            with open('survey_data.json', 'r') as f:
                data = json.load(f)
        else:
            data = []
        with open('survey_data.json', 'w') as f:

            user_data_form = ([{
                'age': form.age.data,
                'social_media': form.social_media.data,
                'password_manager': form.password_manager.data,
                'hacked_before': form.hacked_before.data,
                'email': form.email.data
            }])
            user_data += user_data_form
            data.append(user_data)
            json.dump(data, f, indent=4)
        # Process data (in real app: save to database)
        return redirect(url_for('thank_you'))
    return render_template('survey.html', form=form)


@app.route('/danke')
def thank_you():
    return render_template('thank_you.html')

@app.route('/datenschutz')
def privacy_policy():
    return render_template('datenschutz.html')


if __name__ == '__main__':
    app.run(debug=True, port=43532)