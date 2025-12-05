class Scene:
    def __init__(self, data):
        self.data = data
        self.width = data['canvas_width']
        self.height = data['canvas_height']
        self.canvas_id = data['canvas_id'] 

    def to_dict(self):
        return {
            'canvas_id': self.canvas_id,
            'width': self.width,
            'height': self.height
        }

