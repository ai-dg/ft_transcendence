from .ai import AI
from server.logging import logger

class Paddle:
    def __init__(self, data, user,  ball=None, scene=None,  is_ai=False,side="left" ):
        self.user = user
        self.data = data
        self.is_ai = is_ai
        self.ball = ball
        self.scene = scene
        field = ""
        if side == "left":
            field = 'player_x'
        else:
            field = 'player2_x'
            
        self.x = data[field]
        self.y = data['ai_y'] if is_ai else data['player_y']
        self.width = data['ai_width'] if is_ai else data['player_width']
        self.height = data['ai_height'] if is_ai else data['player_height']
        self.speed = data['ai_speed'] if is_ai else data['player_speed']
        self.direction = 0

        if self.is_ai and self.ball and self.scene:
            self.ai = AI(self, ball, scene, difficulty=self.data['game_param']['level'])
        else:
            self.ai = None

    def set_direction(self, value):
        self.direction = value

    def move(self, canvas_height):
        self.y += self.direction * self.speed

        if self.y < 0:
            self.y = 0
        elif self.y + self.height > canvas_height:
            self.y = canvas_height - self.height

    def move_ai(self, ball):
        if self.ai:
            self.ai.move()

    def reset(self):
        self.y = self.data['ai_y'] if self.is_ai else self.data['player_y']
        self.direction = 0

    def to_dict(self):
        return {
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height
        }
