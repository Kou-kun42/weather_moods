import requests
from flask import Flask, render_template, request, redirect, url_for, session
import pgeocode
from pprint import PrettyPrinter
from dotenv import load_dotenv
import datetime
import os

load_dotenv()
secret_key = os.getenv('SECRET_KEY')
appid = os.getenv('APPID')

app = Flask(__name__)
app.secret_key = secret_key

pp = PrettyPrinter(indent=4)

nomi = pgeocode.Nominatim('us')
url = 'https://api.openweathermap.org/data/2.5/onecall'
datetime = datetime.datetime


@app.route('/', methods=["GET", "POST"])
def home():
    if request.method == "POST":
        session["moods"] = []
        zipcode = request.form.get("zipcode")
        return redirect(url_for("weather", zipcode=zipcode))
    return render_template('home.html')


@app.route('/weather/<zipcode>', methods=["GET", "POST"])
def weather(zipcode):
    if request.method == 'POST':
        for item in request.form.items():
            session["moods"].append(item)
    geo = nomi.query_postal_code(zipcode)
    lat = geo["latitude"]
    lon = geo["longitude"]
    place = geo["place_name"]

    params = {
        "appid": appid,
        "lat": lat,
        "lon": lon,
        "units": "imperial",
        "exclude": "current,minutely,hourly,alerts"
    }

    response = requests.get(url, params=params)
    response_json = response.json()

    daily_weather = []
    for count, day in enumerate(response_json["daily"]):
        if session["moods"]:
            daily_weather.append(
                {
                    "date": datetime.fromtimestamp(day["dt"]).strftime('%m-%d-%Y'),
                    "desc": day['weather'][0]['description'],
                    "high": day['temp']['max'],
                    "low": day['temp']['min'],
                    "day": count,
                    "mood": session["moods"][count][1]
                }
            )
        else:
            daily_weather.append(
                {
                    "date": datetime.fromtimestamp(day["dt"]).strftime('%m-%d-%Y'),
                    "desc": day['weather'][0]['description'],
                    "high": day['temp']['max'],
                    "low": day['temp']['min'],
                    "day": count,
                    "mood": None
                }
            )

    context = {
        "place": place,
        "days": daily_weather
    }

    return render_template('weather.html', **context)


if __name__ == '__main__':
    app.run(debug=True)
