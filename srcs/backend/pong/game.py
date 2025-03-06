import time
from .ball import Ball
from .paddle import Paddle
from .scene import Scene
from .score import Score
from .data import DEFAULT_DATA

class Game:
    def __init__(self, data=None):
        self.data = data if data else DEFAULT_DATA

        self.scene = Scene(self.data)
        self.ball = Ball(self.data)
        self.player = Paddle(self.data, self.ball, self.scene, is_ai=False)
        self.ai = Paddle(self.data, self.ball, self.scene, is_ai=True)
        self.score = Score(self.data)

        self.start_time = time.time()

    def update(self):
        self.player.move(self.scene.height)
        self.ai.move_ai(self.ball)
        self.ai.move(self.scene.height)

        ball_out = self.ball.move(self.scene.width, self.scene.height, [self.player, self.ai])

        elapsed_time = time.time() - self.start_time
        if elapsed_time >= 2:  
            self.ball.increase_speed()
            self.start_time = time.time()  

        if ball_out:
            if self.ball.x <= 0:
                self.score.right += 1

            elif self.ball.x + self.ball.size >= self.scene.width:
                self.score.left += 1
           
            self.ball.reset()
            self.start_time = time.time()

    def to_dict(self):
        return {
            "ball": self.ball.to_dict(),
            "player": self.player.to_dict(),
            "ai": self.ai.to_dict(),
            "scene": self.scene.to_dict(),
            "score": self.score.to_dict(),
        }
