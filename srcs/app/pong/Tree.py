
LEFT = "left"
RIGHT = "right"
PARENT = "parent"




class Tree:
    
    def __init__(self, data):
        self.left = None
        self.right = None
        self.parent = None
        self.game = data

    def add(self, side, node):
        if isinstance(node,Tree):
            if side == "left" and not self.left:
                self.left = node
                node.parent = self
                return {"status": "succes", "message" : "left leaf added"}
            elif side == "right" and not self.right:
                self.right = node
                node.parent = self
                return {"status": "succes", "message" : "right leaf added"}
            else:
                return {"status": "fail", "message" : "invalid parametter : side"}
        else:
            return {"status": "fail", "message" : "invalid parametter : node if not a Tree instance"}
    