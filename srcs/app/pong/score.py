class Score:
    left: int
    right: int
    left_player: str
    right_player: str


    def __init__(self, data):
        self.left = 0
        self.right = 0
        self.left_player = self.get_name("left", data)
        self.right_player = self.get_name("right", data)
        self.canvas_id = data['canvas_id_score']
        self.width = data['canvas_width_score']
        self.height = data['canvas_height_score']

    def setup_names(self, lp, rp):
        self.left_player = lp
        self.right_player = rp

    def to_dict(self):
        return {
            "left": self.left,
            "left_player": self.left_player,
            "right": self.right,
            "right_player": self.right_player,
            "canvas_id": self.canvas_id,
            "width": self.width,
            "height": self.height,
        }
    
    def get_name(self, side, data):
        return data["player1_side"][1] if data["player1_side"][0] == side else data["player2_side"][1] 
