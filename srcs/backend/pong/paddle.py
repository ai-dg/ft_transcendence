from .ai import AI

class Paddle:
    def __init__(self, data, ball=None, scene=None, is_ai=False):
        self.data = data
        self.is_ai = is_ai
        self.ball = ball
        self.scene = scene
        self.x = data['ai_x'] if is_ai else data['player_x']
        self.y = data['ai_y'] if is_ai else data['player_y']
        self.width = data['ai_width'] if is_ai else data['player_width']
        self.height = data['ai_height'] if is_ai else data['player_height']
        self.speed = data['ai_speed'] if is_ai else data['player_speed']
        self.direction = 0

        if self.is_ai and self.ball and self.scene:
            self.ai = AI(self, ball, scene, difficulty="medium")
        else:
            self.ai = None

    def move(self, canvas_height):
        self.y += self.direction * self.speed

        if self.y < 0:
            self.y = 0
        elif self.y + self.height > canvas_height:
            self.y = canvas_height - self.height

    def move_ai(self, ball):
        if self.ai:
            self.ai.move()
        
        # *** Here, basic and simple AI
        # else:
        #     ai_center = self.y + self.height / 2

        #     if ai_center < ball.y - 20:
        #         self.direction = 1
        #     elif ai_center > ball.y + 20:
        #         self.direction = -1
        #     else:
        #         self.direction = 0


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
