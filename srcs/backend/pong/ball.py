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

    def move(self, canvas_width, canvas_height, paddles):
        steps = max(abs(self.speedX), abs(self.speedY))  
        stepX = self.speedX / steps
        stepY = self.speedY / steps

        for _ in range(int(steps)):  
            self.x += stepX
            self.y += stepY

            if self.y <= 0 or self.y + self.size >= canvas_height:
                self.speedY *= -1
                break  

            for paddle in paddles:
                if self.check_collision(paddle):
                    self.speedX *= -1
                    self.x += self.speedX
                    break

        if self.x <= 0 or self.x + self.size >= canvas_width:
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
        self.speedX *= -1  

    def to_dict(self):
        return {
            "x": self.x,
            "y": self.y,
            "size": self.size,
            "speedX": self.speedX,
            "speedY": self.speedY
        }
