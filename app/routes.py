from ast import arguments
import requests
import os
from dotenv import load_dotenv
from flask import Blueprint, jsonify, abort, make_response, request
from datetime import datetime, timezone, timedelta
from time import sleep

load_dotenv()

AARON = os.environ.get("AARONPUUID")
RIOTKEY = os.environ.get("RIOTKEY")

def to_epoch(datetimeobj):
    day_start = datetime(datetimeobj.year,datetimeobj.month,datetimeobj.day, tzinfo=timezone(-timedelta(hours=7)))
    print(day_start)
    return round((day_start - datetime(1970,1,1, tzinfo=timezone.utc)).total_seconds())

def package_match_data(riot_match_data):
    match_time = riot_match_data.json()["info"]["game_datetime"]
    match_time = datetime.fromtimestamp(int(match_time/1000))
    print(match_time)

    player_data = riot_match_data.json()["info"]["participants"]
    
    participants = [player["puuid"] for player in player_data]
    
    i = 0
    while i < len(participants):
        if participants[i] == AARON:
            break
        i += 1
    
    aaron_data = player_data[i]
    aaron_placed = aaron_data["placement"]

    return(
        {
            "match_time": match_time,
            "placed": aaron_placed,
            "win": (aaron_placed < 5),
            "players_eliminated": aaron_data["players_eliminated"],
            "total_damage": aaron_data["total_damage_to_players"]
        }
        )



riot_bp = Blueprint('riot_bp', __name__, '/TFT')

@riot_bp.route('/aaron', methods=['GET'])
def get_today_matches():
    riot_data = requests.get(f'https://americas.api.riotgames.com/tft/match/v1/matches/by-puuid/{AARON}/ids', 
    params = {
        # "startTime": to_epoch(datetime.now())
        # for testing:
        "startTime": to_epoch(datetime(2022,6,12))
    },
    headers={
        "X-Riot-Token":RIOTKEY
    })
    print(to_epoch(datetime.today()))
    return jsonify(riot_data.json())

@riot_bp.route('/aaron/<match_id>', methods=['GET'])
def get_match_data(match_id):
    riot_match_data = requests.get(f'https://americas.api.riotgames.com/tft/match/v1/matches/{match_id}', 
    headers={
        "X-Riot-Token":RIOTKEY
    })
    msg = package_match_data(riot_match_data)

    return make_response(jsonify(msg), 200)

@riot_bp.route('/aaron/recent-matches', methods=['GET'])
def get_recent_matches():
    query_params = request.args.to_dict()
    if "num_matches" in query_params:
        num_matches = query_params["num_matches"]
    else:
        num_matches = 10
    riot_data = requests.get(f'https://americas.api.riotgames.com/tft/match/v1/matches/by-puuid/{AARON}/ids', 
    params = {
        "count": num_matches
    },
    headers={
        "X-Riot-Token":RIOTKEY
    })

    return jsonify(riot_data.json())


@riot_bp.route('/aaron/matches', methods=['GET'])
def get_multiple_match_data():
    arguments = request.args.to_dict(flat=False)

    matches = arguments.get('match')
    print(matches)
    match_data = {}
    for match in matches:
        riot_match_data = requests.get(
            f'https://americas.api.riotgames.com/tft/match/v1/matches/{match}', 
            headers={"X-Riot-Token":RIOTKEY}
            )

        match_data[match] = package_match_data(riot_match_data)
        sleep(.2)

    return make_response(jsonify(match_data), 200)
