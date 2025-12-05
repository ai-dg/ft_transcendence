from server.logging import logger
import asyncio
from server.asyncredis import redis
from .tools import move_game_to, create_new_game, lock_tournament_game, get_unseted_tournament_game, RUNNING_GAMES, PENDING_GAMES
from .data import setup_game_data
from .game import Game
from .Tree import Tree, LEFT, RIGHT
import uuid

def debug_tree(tree, depth=0):
    if not tree:
        return
    logger.info("  " * depth + f"- {game_status(tree.game)}")
    debug_tree(tree.left, depth + 1)
    debug_tree(tree.right, depth + 1)


async def game_status(game):
        if game:
            return await game.get_status()
        return None


async def setup_game(tree):
    player1 = tree.left.game.winner
    player2 = tree.right.game.winner
    game = await lock_tournament_game(tree.game.game_uid, player1=player1, player2=player2) 
    move_game_to(tree.game.game_uid, PENDING_GAMES, RUNNING_GAMES)
    # attention l'ordre des important
    logger.info(f"TRACKER              GAME DATABEFORE SETTING UP GAME      {game}")
    await tree.game.setup_game(game)

    logger.info(f"TRACKER              GAME DATA        {tree.game.data}")
    await tree.game.set_status("in_progress")
    return tree.game


async def all_games_played(tree):
    if tree and await game_status(tree.game) == "finished":
        return True
    return False


async def get_next_game(tree):
    if tree and await game_status(tree.game) == "ready":
        await tree.game.set_status("in_progress")
        return tree.game
    if tree and await game_status(tree.game) == "finished":
        return None
    if tree and await game_status(tree.game) == "waiting":
        statuses = await asyncio.gather(
            game_status(tree.left.game),
            game_status(tree.right.game)
        )
        if all(status == "finished" for status in statuses):
            return await setup_game(tree)
        if tree.left and await game_status(tree.left.game) == "ready":
            await tree.left.game.set_status("in_progress")
            return tree.left.game
        if tree.right and await game_status(tree.right.game) == "ready":
            await tree.right.game.set_status("in_progress")
            return tree.right.game
        if tree.left and await game_status(tree.left.game) == "waiting":
            return await get_next_game(tree.left)
        if tree.right and await game_status(tree.right.game) == "waiting":
            return await get_next_game(tree.right)
    return None


async def collect_data(tree):
    return await tree.game.get_match_stats()


async def exec_in_tree(tree, func, coll):
    if tree:
        coll.append(await func(tree))
    if tree.left:
        await exec_in_tree(tree.left, func, coll)
    if tree.right:
        await exec_in_tree(tree.right, func, coll)


async def get_tournament_stats(tree):
    stats = {}
    stats["winner"] = await tree.game.get_winner()
    coll = []
    await exec_in_tree(tree, collect_data, coll)
    stats["games"] = coll
    return stats


class Tournament:
    
    def __init__(self, params):
        self.params = params
        self.finished_games = []
        self.ready_games = []
        self.running_games = []
        self.tree = None
        self.tournament_uid = params.get("tournament_uid")
        self.players = params.get("players")
        self.win_condition = params.get("win_condition")
        self.max_pts = params.get("max_pts")
        self.level = params.get("level")

    async def init_tournament(self):
        await self.setup_tournament_tree()
        #self.log_tournament_tree(self.tree)

    def log_match_detail(self, match_data, deep):
        data = f"{deep * ' '}({match_data.p1name} vs {match_data.p2name})"
        logger.info(data)

    def log_tournament_tree(self, tree, deep=0):
        if deep == 0:
            logger.info("created tree :")
        if tree and tree.game:
            self.log_match_detail(tree.game, deep)
        else:
            logger.info("Game not created yet")
        if tree.left :
            self.log_tournament_tree(tree.left, deep+1)
        if tree.right :
            self.log_tournament_tree(tree.right, deep+1)
 

    def get_next_player(self):
        """
            retire et renvoie un joueur a chaque appel jusqu'a ce que la liste soit vide
        """
        if self.players_left:
            return self.players_left.pop(0)
        return None


    async def setup_tournament_tree(self):
        """

        Etape 1, nous récupérons tous les joueurs et 
        construisons un noeud pour chaque partie possible a l'initialisation a 
        l'aide de la fonction prepare_game, a laquelle nous passons les noms des joueurs
        puis appelons la fonction qui va construire l'arbre    
        """

        self.players_left = self.players.copy()
        self.total_players = len(self.players)
        games = self.total_players / 2
        trees = []
        while games :
            games -=1
            player1 = self.get_next_player()
            player2 = self.get_next_player()
            if (player1 and player2):
                players = (player1, player2)
                tree = Tree(await self.prepare_game(players))
                trees.append(tree)
            else:
                return
        self.tree = await self.build_tree(trees)
        
    async def build_tree(self, trees):
        """
            Nous récupérons une liste de parties jouables, et construisons l'arbre.
            nous construisont un parent pour chaque 2 noeuds...
            et rappelons la fonction de façon récursive. 
            S'il n'y a qu'un seul noeud nous renvoyons l'arbre
        """
        new_trees = []
        if len(trees) > 1:
            for i in range (0, len(trees), 2):
                tree = Tree(await self.prepare_game())
                tree.add(LEFT, trees[i])
                tree.add(RIGHT, trees[i + 1])
                new_trees.append(tree)
            return await self.build_tree(new_trees)
        return trees[0]


    async def prepare_game(self, players=("pending", "pending")):
        """
            cette fonction prépare les paramettres de jeu pour chaque partie...
            s'il s'agit n'un noeud parent initial, la partie s'initialise avec des données incompletes 
            qui doivent par la suite se completer en initialisant game
        
        """
        game_uid = str(uuid.uuid4())
        height = self.params.get("canvas_height")
        width = self.params.get("canvas_width")
        if not width:
            width = "800px"
        if not height:
            height = "400px"
        status = "waiting" if any (p =="pending" for p in players) else "ready"
 
        game_data = {
            "canvas_height" : height,
            "canvas_width" : width, 
            "from_tournament": True,
            "tournament_uid" : self.tournament_uid,
            "game_param" : self.params.get("game_param"),
            "status": status,
            "game_uid": game_uid,
            "created_by": self.params.get("created_by"),
            "player1": players[0],
            "player2": players[1],
            "players": [players[0], players[1]],
            "allowed_users" : [players[0], players[1]],
            "opponent" : "remote"}
        await create_new_game(game_data, game_uid)
        if status == "ready":
            logger.info("SETTED")
            await lock_tournament_game(game_uid)
            game_param = await setup_game_data(game_uid)
        else : 
            logger.info("UNSETTED")
            await get_unseted_tournament_game(game_uid)
            # je récup un objet temporaire...
            game_param = await setup_game_data(game_uid) 
        game_param["status"] = status
        logger.info(f"TRACKER PREPARE GAME : {game_param}")
        game = Game(game_param)
        await game.setup_game(game_param)
        return game
    
    async def set_game_finished(self):
        pass
