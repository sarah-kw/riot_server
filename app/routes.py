import requests
import os
from dotenv import load_dotenv
from flask import Blueprint, jsonify, abort, make_response, request
from datetime import datetime, timezone, timedelta

load_dotenv()

AARON = os.environ.get("AARONPUUID")
RIOTKEY = os.environ.get("RIOTKEY")

def to_epoch(datetimeobj):
    day_start = datetime(datetimeobj.year,datetimeobj.month,datetimeobj.day, tzinfo=timezone(-timedelta(hours=7)))
    print(day_start)
    return round((day_start - datetime(1970,1,1, tzinfo=timezone.utc)).total_seconds())


riot_bp = Blueprint('riot_bp', __name__, '/TFT')

@riot_bp.route('/aaron', methods=['GET'])
def get_today_matches():
    riot_data = requests.get(f'https://americas.api.riotgames.com/tft/match/v1/matches/by-puuid/{AARON}/ids', 
    params = {
        "startTime": to_epoch(datetime.now())
    },
    headers={
        "X-Riot-Token":RIOTKEY
    })
    print(to_epoch(datetime.today()))

    return jsonify(riot_data.json())

@riot_bp.route('/aaron/<match_id>', methods=['GET'])
def get_match_data(match_id):
    riot_match_data =requests.get(f'https://americas.api.riotgames.com/tft/match/v1/matches/{match_id}', 
    params = {
        "startTime": to_epoch(datetime.now())
    },
    headers={
        "X-Riot-Token":RIOTKEY
    })

    player_data = riot_match_data.json()["info"]["participants"]
    
    participants = [player["puuid"] for player in player_data]
    
    i = 0
    while i < len(participants):
        if participants[i] == AARON:
            break
        i += 1
    
    aaron_data = player_data[i]
    aaron_placed = aaron_data["placement"]
    msg = {
        "placed": aaron_placed,
        "win": (aaron_placed < 5),
        "players_eliminated": aaron_data["players_eliminated"],
        "total_damage": aaron_data["total_damage_to_players"]
    }

    return jsonify(msg)

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

