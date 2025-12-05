# It sends the time to transfert the data in websocketing, time in ms
from server.logging import logger

from .tools import update_game_params, get_game_param, RUNNING_GAMES, RUNNING_TOURNAMENTS

seconds_to_refresh = 0.005

# Pixels/secondes
ball_speedX_real = 700
ball_speedY_real = 700
player_speed_real = 800
ai_speed_real = 400

DEFAULT_DATA = {

    "is_ai": True,
    "is_local": False,


    # Scene (Canvas)
    "canvas_id": "gameCanvas",
    "canvas_width": 800,
    "canvas_height": 400,

    # Ball
    "ball_x": 400,
    "ball_y": 205,
    "ball_size": 13,
    "ball_speedX": ball_speedX_real * seconds_to_refresh,
    "ball_speedY": ball_speedY_real * seconds_to_refresh,

    # Paddle (Player)
    "player_x": 10,
    "player_y": 150,
    "player_width": 10,
    "player_height": 100,
    "player_speed": player_speed_real * seconds_to_refresh,
    "player_direction": 0,

        # Paddle (Player 2)
    "player2_x": 780,
    "player2_y": 150,
    "player2_width": 10,
    "player2_height": 100,
    "player2_speed": player_speed_real * seconds_to_refresh,
    "player2_direction": 0,

    # Paddle (IA)
    "ai_x": 780,
    "ai_y": 150,
    "ai_width": 10,
    "ai_height": 100,
    "ai_speed": ai_speed_real * seconds_to_refresh,
    "ai_direction": 0,

    # Score
    "canvas_id_score": "scoreCanvas",
    "canvas_width_score": 400,
    "canvas_height_score": 150,
}


exemple = {
    'players': 2, 
    'game_param': {'opponent': "remote",
                    'player': 2, 
                    'max_pts': 50, 
                    'win_condition': 10,
                    'level': 'none'},
    'status': 'ready', 
    'game_uid': "4775c859-e76d-4ed7-bac5-27ce1c206345", 
    'type': "new_game", 
    'created_by': "diego",
    'player1':'diego',
    'player2': "chris",
    'left': "diego",
    'right': "chris",
    'allowed_users': ["diego", "chris"]}


async def setup_tournament_data(tournament_uid):
    params = await get_game_param(tournament_uid)
    dataset = {**DEFAULT_DATA, **params}
    dataset["allowed_users"] = []
    logger.info(f"TRACKER SETUP TOUNAMENT : {dataset}")
    await update_game_params(tournament_uid, dataset)
    return dataset


async def setup_game_data(game_uid):
    params = await get_game_param(game_uid)
    dataset = {}




    dataset = {
        "created_by": params["created_by"],
        "player1" : params ["player1"],
        "player2": params["player2"],
        "max_pts": params["game_param"]["max_pts"],
        "win_condition": params["game_param"]["win_condition"],
        "level": params["game_param"]["level"],
        "opponent": params["game_param"]["opponent"],
        "game_param": params["game_param"],
        "game_uid": params["game_uid"],

        # Scene (Canvas)
        "canvas_id": "gameCanvas",
        "canvas_width": 800,
        "canvas_height": 400,

        # Ball
        "ball_x": 400,
        "ball_y": 205,
        "ball_size": 13,
        "ball_speedX": ball_speedX_real * seconds_to_refresh,
        "ball_speedY": ball_speedY_real * seconds_to_refresh,

        # Paddle (Player)
        "left": params["left"],
        "player_x": 10,
        "player_y": 150,
        "player_width": 10,
        "player_height": 100,
        "player_speed": player_speed_real * seconds_to_refresh,
        "player_direction": 0,

            # Paddle (Player 2)
        "right":params["right"],
        "player2_x": 780,
        "player2_y": 150,
        "player2_width": 10,
        "player2_height": 100,
        "player2_speed": player_speed_real * seconds_to_refresh,
        "player2_direction": 0,

        # Paddle (IA)
        "ai_x": 780,
        "ai_y": 150,
        "ai_width": 10,
        "ai_height": 100,
        "ai_speed": ai_speed_real * seconds_to_refresh,
        "ai_direction": 0,

        # Score
        "canvas_id_score": "scoreCanvas",
        "canvas_width_score": 400,
        "canvas_height_score": 150,
        }
    
    if "allowed_users" in params:
        dataset["allowed_users"] = params["allowed_users"]
    else:
        dataset["allowed_users"] = [params["player1_side"][1], params["player2_side"][1]]
    if  params["player1_side"]:
        dataset["player1_side"] = params["player1_side"]
    if  params["player2_side"]:
        dataset["player2_side"] = params["player2_side"]
    
    if params["game_param"]["opponent"] == 'remote':
        dataset["is_ai"] = False
        dataset["is_local"] = False

    if params["game_param"]["opponent"] == 'ai':
        dataset["is_ai"] = True
        dataset["is_local"] = False
    if params["game_param"]["opponent"] == 'invited':
        dataset["is_ai"] = False
        dataset["is_local"] = True

    if params["tournament_uid"]:
        dataset["tournament_uid"] = params["tournament_uid"]
    else : 
        dataset["tournament_uid"] = False

    dataset["status"] = "ready"

    #if dataset["tournament_uid"] == False:
    await update_game_params(game_uid, dataset)



    return dataset