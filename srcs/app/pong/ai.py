import random
import time
from server.logging import logger

class AI:
    def __init__(self, paddle, ball, scene, difficulty="medium"):
        self.paddle = paddle
        self.ball = ball
        self.canvas_height = scene.height
        self.difficulty = difficulty
        self.error_rate = {
            "easy": 0.2,
            "medium": 0.1,
            "hard": 0.05,
            "impossible": 0.01
        }.get(difficulty)

        
        self.reaction_delay = {
            "easy": 0.3,
            "medium": 0.2,
            "hard": 0.1,
            "impossible": 0.05
        }.get(difficulty)

        self.last_direction = 0  
        self.last_move_time = 0  

        logger.info(f"☯️ ​ Difficulty: {self.difficulty}, error_rate: {self.error_rate}, reaction_delay: {self.reaction_delay}")

    def predict_ball_position(self):
        predicted_y = self.ball.y
        speed_y = self.ball.speedY

        while True:
            predicted_y += speed_y

            if predicted_y < 0:
                predicted_y = -predicted_y
                speed_y = -speed_y
            elif predicted_y > self.canvas_height:
                predicted_y = 2 * self.canvas_height - predicted_y
                speed_y = -speed_y
            else:
                break
        
        return predicted_y

    def move(self):
        current_time = time.time()
        ai_center = self.paddle.y + self.paddle.height / 2
        target_y = self.predict_ball_position()
        if (self.paddle.x > self.ball.x and self.ball.speedX > 0) or (self.paddle.x < self.ball.x and self.ball.speedX < 0):            
            if current_time - self.last_move_time > self.reaction_delay:
                if ai_center < target_y - 20:
                    self.last_direction = 1  
                elif ai_center > target_y + 20:
                    self.last_direction = -1  
                else:
                    self.last_direction = 0                  
                if random.random() < self.error_rate:
                    self.last_direction = random.choice([-1, 0, 1])
                
                self.last_move_time = current_time

            self.paddle.direction = self.last_direction
        else:            
            self.paddle.direction = 0  
        self.paddle.move(self.canvas_height)
