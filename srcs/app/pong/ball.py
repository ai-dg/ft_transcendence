import random
import math
import time

class Ball:
    def __init__(self, data):            
        self.data = data
        self.x = data['ball_x']
        self.y = data['ball_y']
        self.size = data['ball_size']
        self.base_speedX = data['ball_speedX']  
        self.base_speedY = data['ball_speedY']
        self.speedX = self.base_speedX
        self.speedY = self.base_speedY

    
    def angle_paddle(self, paddle):
        ball_center = self.y + self.size / 2
        paddle_center = paddle.y + paddle.height / 2

        # Si intersect = 0, il touche au centre de la raquette
        # Si < 0, en haut
        # Si > 0, en bas
        relative_intersect = (ball_center - paddle_center)
        # Transformer intersect en 0, 1 ou -1
        normalized = relative_intersect / (paddle.height / 2)
        # Eviter le depassement de ces valeurs
        normalized = max(-1, min(1, normalized))

        max_angle = math.radians(60)
        angle = normalized * max_angle

        speed = math.hypot(self.speedX, self.speedY)

        if self.speedX > 0:
            direction = -1
        else:
            direction = 1

        self.speedX = direction * speed * math.cos(angle)
        self.speedY = speed * math.sin(angle)

        self.x += self.speedX

    def random_angles(self):
        angle_deg = random.choice([30, 45, 60])
        angle_rad = math.radians(angle_deg)
        speed = math.hypot(self.speedX, self.speedY)

        if self.speedX > 0:
            direction = -1
        else:
            direction = 1

        self.speedX = direction * speed * math.cos(angle_rad)
        self.speedY = speed * math.sin(angle_rad)

        self.x += self.speedX


    def move(self, canvas_width, canvas_height, paddles):
        steps = max(abs(self.speedX), abs(self.speedY))  
        stepX = self.speedX / steps
        stepY = self.speedY / steps

        for _ in range(int(steps)):  
            self.x += stepX
            self.y += stepY

            if self.y <= 0 or self.y + self.size >= canvas_height :
                self.speedY *= -1
                break  

            for paddle in paddles:
                if self.check_collision(paddle):
                    self.angle_paddle(paddle)
                    break

        if self.x < -15 or self.x + self.size >= canvas_width + 15:
            return True  
        return False  

    def check_collision(self, paddle):
        return (
            self.x < paddle.x + paddle.width and
            self.x + self.size > paddle.x and
            self.y + self.size > paddle.y and
            self.y < paddle.y + paddle.height
        )

    def increase_speed(self):
        speed_multiplier = 1.05  
        self.speedX *= speed_multiplier
        self.speedY *= speed_multiplier

    def reset(self):
        self.x = self.data['ball_x']
        self.y = self.data['ball_y']
        self.speedX = self.base_speedX
        self.speedY = self.base_speedY
        self.random_angles()
        self.speedX *= random.choice([-1, 1])

    def to_dict(self):
        return {
            "x": self.x,
            "y": self.y,
            "size": self.size,
            "speedX": self.speedX,
            "speedY": self.speedY
        }
