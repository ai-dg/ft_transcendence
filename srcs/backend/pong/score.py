class Score:
    left: int
    right: int

    def __init__(self, data):
        self.left = 0
        self.right = 0
        self.canvas_id = data['canvas_id_score']
        self.width = data['canvas_width_score']
        self.height = data['canvas_height_score']

    def to_dict(self):
        return {
            "left": self.left,
            "right": self.right,
            "canvas_id": self.canvas_id,
            "width": self.width,
            "height": self.height,
        }
