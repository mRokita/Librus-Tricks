from flask import Flask, render_template, request
from librus_tricks import minified_login, create_session, exceptions, cache
from librus_tricks.tools import subjects_averages, percentage_average

app = Flask(__name__)


@app.route('/')
def home_view():
    return render_template('home.html')


@app.route('/calc', methods=['POST'])
def count_averages():
    try:
        session = create_session(request.json['email'], request.json['password'], cache=cache.DumbCache())
    except exceptions.LibrusPortalInvalidPasswordError:
        return render_template('bad_password.html')
    except exceptions.CaptchaRequired:
        return render_template('damn_captcha.html')
    return render_template('table.html',
                           averages=subjects_averages(session.grades_categorized),
                           percentages=percentage_average(session.grades()))

if __name__ == '__main__':
    app.run()
