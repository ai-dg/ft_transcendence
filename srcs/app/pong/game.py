import time
from .ball import Ball
from .paddle import Paddle
from .scene import Scene
from .score import Score
from .data import DEFAULT_DATA
from .tools import get_pseudo_or_user
from asgiref.sync import sync_to_async
import secrets

{'players': 2, 
 'game_param': 
 {'opponent': 'remote', 
  'player': 2, 
  'max_pts': 50, 
  'win_condition': 10, 
  'level': 'none'},
    'status': 'ready', 
    'game_uid': '93bd5ea8-bb42-4abc-a738-eba371ea9ab9', 
    'type': 'new_game', 
    'created_by': 'chris', 
    'player1': 'chris', 
    'player2': 'diego', 
    'left': 'chris', 
    'right': 'diego', 
    'allowed_users': ['chris', 'diego']}


class Game:
    def __init__(self, data=None):
        self.running = False
        self.data = data if data else DEFAULT_DATA
        self.p1name = "pending"
        self.p2name = "pending"

        self.waiting_for_reset = False
        self.reset_resume_time = None


        self.game_uid = self.data.get("game_uid")
        if "win_condition" in data['game_param']:
            self.win_condition = int(data['game_param']["win_condition"])
        else:
            self.win_condition = 10
        if "max_pts" in data['game_param']:
            self.max_pts = int(data['game_param']["max_pts"])
        else:
            self.max_pts = 30
        if "level" in data['game_param']:
            self.level = data['game_param']["level"]
        self.scene = Scene(self.data)
        self.ball = Ball(self.data)
        self.winner = None
        # if self.data["status"] == "ready":
        #     await self.setup()

    async def setup_game(self, data):
        self.data = data
        await self.setup()


    async def setup(self):
        if self.data["player1_side"][1] :
            self.p1name = self.data["player1_side"][1]
        if self.data["player2_side"][1] :
            self.p2name = self.data["player2_side"][1]
        is_p1_ai = self.p1name == "ai"
        is_p2_ai = self.p2name == "ai"
        if self.data["player1_side"][0] == "left":
            self.player = Paddle(self.data, self.p1name, self.ball, self.scene, is_ai=is_p1_ai, side="left")
            self.player2 = Paddle(self.data, self.p2name, self.ball, self.scene, is_ai=is_p2_ai, side="right")
        else:
            self.player = Paddle(self.data, self.p1name, self.ball, self.scene, is_ai=is_p1_ai, side="right")  
            self.player2 = Paddle(self.data, self.p2name, self.ball, self.scene, is_ai=is_p2_ai, side="left")
        self.score = Score(self.data)
        await self.set_pseudo()
        self.start_time = time.time()

    async def is_match_over(self):
        right_win = self.score.right >= self.score.left + self.win_condition or self.score.right == self.max_pts 
        left_win = self.score.left >= self.score.right + self.win_condition or self.score.left == self.max_pts
        if right_win or left_win:
            self.data["status"] = "finished"
            winner = ""
            if self.score.left > self.score.right:
                winner = self.data["left"]
            else:
                winner = self.data["right"]
            self.winner = winner
            return True
        return False
    
    async def get_status(self):
        return self.data["status"]
    
    async def set_status(self, status):
        self.data["status"] = status

    async def get_winner(self):
        return self.winner

    async def get_match_stats(self):
        p1score = None
        p2score = None
        p1side = None
        p2side = None
        p1pseudo = None
        p2pseudo = None
        if self.data['left'] == self.p1name:
            p1score = self.score.left
            p1pseudo = self.score.left_player if self.score.left_player != self.p1name else None
            p1side = "left"
            p2score = self.score.right
            p2pseudo = self.score.right_player if self.score.right_player != self.p2name else None
            p2side = "right"
        else : 
            p1score = self.score.right
            p1pseudo = self.score.right_player if self.score.right_player != self.p1name else None
            p1side = "right"
            p2score = self.score.left
            p2pseudo = self.score.left_player if self.score.left_player != self.p2name else None
            p2side = "left"
        stats = {
            "player1": {
                "name" : self.p1name,
                "pseudo" : p1pseudo, 
                "score": p1score,
                "side" : p1side
            },
            "player2": {
                "name" : self.p2name, 
                "pseudo" : p2pseudo,   
                "score": p2score,
                "side" : p2side
            }, 
            "winner" : self.winner
        }
        return stats
    
    async def set_pseudo(self):
        from_tournament = self.data.get("tournament_uid")
        if from_tournament:
            lp = self.data.get("left")
            rp = self.data.get("right")
            lp = await get_pseudo_or_user(lp)
            rp = await get_pseudo_or_user(rp)
            self.score.setup_names(lp, rp)

    async def update(self):
        # Gestion du délai après un point marqué
        if self.waiting_for_reset:
            if time.time() >= self.reset_resume_time:
                self.ball.reset()
                self.start_time = time.time()
                self.waiting_for_reset = False
            else:
                # Pendant la pause, les paddles peuvent encore bouger
                self.player.move(self.scene.height)
                self.player2.move_ai(self.ball)
                self.player2.move(self.scene.height)
            return

        # Mouvements normaux
        self.player.move(self.scene.height)
        self.player2.move_ai(self.ball)
        self.player2.move(self.scene.height)

        ball_out = self.ball.move(self.scene.width, self.scene.height, [self.player, self.player2])

        elapsed_time = time.time() - self.start_time
        if elapsed_time >= 2:  
            self.ball.increase_speed()
            self.start_time = time.time()  

        if ball_out:
            if self.ball.x <= 0:
                self.score.right += 1
            elif self.ball.x + self.ball.size >= self.scene.width:
                self.score.left += 1

            # Démarre un timer pour réinitialiser la balle plus tard
            self.waiting_for_reset = True
            self.reset_resume_time = time.time() + 2


    async def to_dict(self):
        score = self.score.to_dict()

        return {
            "ball": self.ball.to_dict(),
            "player": self.player.to_dict(),
            "player2": self.player2.to_dict(),
            "scene": self.scene.to_dict(),
            "score": score,
        }
