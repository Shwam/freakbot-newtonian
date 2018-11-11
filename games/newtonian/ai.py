# This is where you build your AI for the Newtonian game.

from joueur.base_ai import BaseAI

# <<-- Creer-Merge: imports -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
# you can add additional import(s) here

from colorama import init, Fore, Back, Style
import heapq
import time

# <<-- /Creer-Merge: imports -->>

enemy = None
    
counters = {"intern":"manager", "physicist":"intern", "manager":"physicist"} # manager is counters[intern]
countered_by = {"manager":"intern", "intern":"physicist", "physicist":"manager"} # intern is countered_by[manager]

def radius(tile, r=1):
    frontier = [tile]
    tiles = set()
    while r >= 0:
        r -= 1
        tiles |= frontier
        if r >= 0:
            for t in frontier:
                frontier = t.get_neighbors()
    return tiles

def manhattan(t1, t2):
    return abs(t1.x-t2.x) + abs(t1.y-t2.y)

def walkable(t, goal):
    return {n for n in t.get_neighbors() if ((n.is_pathable() and not n.unit and (not n.owner or not n.owner.id == enemy)) or goal(n))}

def neighbors(t, goal):
    return {t for t in t.get_neighbors()}

class AI(BaseAI):
    """ The AI you add and improve code inside to play Newtonian. """

    @property
    def game(self):
        """The reference to the Game instance this AI is playing.

        :rtype: games.newtonian.game.Game
        """
        return self._game  # don't directly touch this "private" variable pls

    @property
    def player(self):
        """The reference to the Player this AI controls in the Game.

        :rtype: games.newtonian.player.Player
        """
        return self._player  # don't directly touch this "private" variable pls

    def get_name(self):
        """ This is the name you send to the server so your AI will control the
            player named this string.

        Returns
            str: The name of your Player.
        """
        # <<-- Creer-Merge: get-name -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
        return "FreakBot" # REPLACE THIS WITH YOUR TEAM NAME
        # <<-- /Creer-Merge: get-name -->>

    def start(self):
        """ This is called once the game starts and your AI knows its player and
            game. You can initialize your AI here.
        """
        # <<-- Creer-Merge: start -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
        # replace with your start logic

        # Un-comment this line if you are using colorama for the debug map.
        #init()
        enemy = self.player.opponent.id

        # <<-- /Creer-Merge: start -->>

    def game_updated(self):
        """ This is called every time the game's state updates, so if you are
        tracking anything you can update it here.
        """
        # <<-- Creer-Merge: game-updated -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
        # replace with your game updated logic
        # <<-- /Creer-Merge: game-updated -->>

    def end(self, won, reason):
        """ This is called when the game ends, you can clean up your data and
            dump files here if need be.

        Args:
            won (bool): True means you won, False means you lost.
            reason (str): The human readable string explaining why your AI won
            or lost.
        """
        # <<-- Creer-Merge: end -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
        # replace with your end logic
        # <<-- /Creer-Merge: end -->>

    def cost_map(self, unit):
        cost = dict()
        for tile in self.game.tiles:
            cost[tile] = 0
            if tile.unit and tile.unit.owner != self.player:
                for t in radius(tile, 5):
                    cost[tile] += 1 if counters[tile.unit.job.title] == unit.job.title else -1 if countered_by[tile.unit.job.title] == unit.job.title else 0
                    

    def act(self, unit, enable_attack=True):
        if unit.acted:
            return True
        if unit.job.title == 'physicist':
            for t in unit.tile.get_neighbors() + [unit.tile]:
                if t.machine and t.blueium_ore + t.redium_ore >= t.machine.refine_input and unit.act(t):
                    while not unit.acted and t.blueium_ore + t.redium_ore >= t.machine.refine_input:
                        unit.act(t)
                    return True
                if t.unit and t.unit.owner != unit.owner and t.unit.health > 0:
                    if (t.unit.job.title == "manager" and t.unit.stun_time == 0 and t.unit.stun_immune == 0 and unit.act(t)):
                        if unit.acted:
                            return True
                    if (enable_attack and unit.moves >= unit.job.moves and unit.attack(t)):
                        return True
        elif unit.job.title == 'intern':
            for t in unit.tile.get_neighbors() + [unit.tile]:
                if t.owner != self.player.opponent and t.machine:
                    if unit.blueium_ore > 0 and t.machine.ore_type == "blueium" and unit.drop(t, 0, 'blueium ore'):
                        pass
                    if unit.redium_ore > 0 and t.machine.ore_type == "redium" and unit.drop(t, 0, 'redium ore'):
                        pass
                if (t.owner == self.player.opponent or not t.machine) and unit.blueium_ore + unit.redium_ore < unit.job.carry_limit:
                    if t.blueium_ore > 0 and unit.pickup(t, 0, 'blueium ore'):
                        pass
                    if t.redium_ore > 0 and unit.pickup(t, 0, 'redium ore'):
                        pass
                if t.unit and t.unit.owner != unit.owner and t.unit.health > 0:
                    if (t.unit.job.title == "physicist" and t.unit.stun_time == 0 and t.unit.stun_immune == 0 and unit.act(t)):
                        if unit.acted:
                            return True
                    if (enable_attack and unit.moves >= unit.job.moves and unit.attack(t)):
                        return True
        elif unit.job.title == 'manager':
            for t in unit.tile.get_neighbors() + [unit.tile]:
                if t in self.player.generator_tiles:
                    if unit.blueium > 0 and unit.drop(t, 0, 'blueium'):
                        pass
                    if unit.redium > 0 and unit.drop(t, 0, 'redium'):
                        pass
                if unit.redium + unit.blueium < unit.job.carry_limit:
                    if t.blueium and unit.pickup(t, 0, 'blueium'):
                        pass
                    if t.redium and unit.pickup(t, 0, 'redium'):
                        pass
                if t.unit and t.unit.owner != unit.owner and t.unit.health > 0:
                    if (t.unit.job.title == "intern" and t.unit.stun_time == 0 and t.unit.stun_immune == 0 and unit.act(t)):
                        if unit.acted:
                            return True
                    if (enable_attack and unit.moves >= unit.job.moves and unit.attack(t)):
                        return True
        return False

    def do_stuff(self, unit):
        if unit is not None and unit.tile is not None and unit.stun_time <= 0 and not unit.acted and unit.moves:
            if unit.job.title == 'physicist':
                goal = lambda tile: tile.machine and tile.blueium_ore + tile.redium_ore >= tile.machine.refine_input
                path = self.a_star(unit.tile, goal, successor=walkable)
                # move toward a machine if there's one with unrefined ores
                while unit.moves > 0 and path:
                    if self.act(unit):
                        return True
                    if not unit.move(path.pop()):
                        break
                
                if not any([goal(m.tile) for m in self.game.machines]):
                    # go harass a manager
                    goal = lambda tile: tile.unit and tile.unit.owner != self.player and tile.unit.job.title == "manager"
                    path = self.a_star(unit.tile, goal, successor=walkable)
                    while unit.moves > 0 and path:
                        if self.act(unit):
                            return True
                        if not unit.move(path.pop()):
                            break

                self.act(unit)

            elif unit.job.title == 'intern':
                if unit.blueium_ore + unit.redium_ore < unit.job.carry_limit:
                    # gather resources
                    goal = lambda tile: tile.blueium_ore+tile.redium_ore > 0 and tile.machine is None
                    path = self.a_star(unit.tile, goal, successor=walkable, goal_impassible=False)
                    while unit.moves > 0 and path:
                        if self.act(unit):
                            return True
                        if not unit.move(path.pop()):
                            break
                else:
                    # return to reactor
                    goal = lambda tile: tile.owner != self.player.opponent and tile.machine and (tile.machine.ore_type == "blueium" and unit.blueium_ore > 0 or tile.machine.ore_type == "redium" and unit.redium_ore > 0)
                    path = self.a_star(unit.tile, goal, successor=walkable)
                    while unit.moves > 0 and path:
                        if self.act(unit):
                            return True
                        if not unit.move(path.pop()):
                            break
                self.act(unit)

            elif unit.job.title == 'manager':
                goal = lambda tile: (tile.blueium or tile.redium)
                gimp = True

                if unit.blueium + unit.redium < unit.job.carry_limit and any([goal(t) for t in self.game.tiles]):
                    # seek refined ore
                    goal = lambda tile: (tile.blueium or tile.redium)
                elif unit.blueium + unit.redium >= unit.job.carry_limit:
                    # take to generator
                    goal = lambda tile: tile in self.player.generator_tiles
                    gimp = False
                else:
                    # harass interns
                    goal = lambda tile: tile.unit and tile.unit.owner != self.player and tile.unit.health > 0 and tile.unit.job.title == "intern"
                path = self.a_star(unit.tile, goal, successor=walkable, goal_impassible=gimp)
                while unit.moves > 0 and path:
                    if self.act(unit, enable_attack=gimp):
                        return True
                    if not unit.move(path.pop()):
                        break
                self.act(unit)

    def run_turn(self):
        """ This is called every time it is this AI.player's turn.

        Returns:
            bool: Represents if you want to end your turn. True means end your turn, False means to keep your turn going and re-call this function.
        """
        # <<-- Creer-Merge: runTurn -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
        # Put your game logic here for runTurn

        #self.display_map()
        for unit in self.player.units:
            if self.player.time_remaining < 10**6:
                return True
            self.do_stuff(unit)
        for unit in self.player.units:
            if self.player.time_remaining < 10**6:
                return True
            if not unit.acted:
                self.do_stuff(unit)
        
        return True
        # <<-- /Creer-Merge: runTurn -->>

    def a_star(self, start, goal, successor=neighbors, cost=manhattan, heuristic = lambda x: 0, goal_impassible=True):
        path = []

        if not any([goal(tile) for tile in self.game.tiles]):
            return path

        closed = set()
        parent = {}
        fringe = []
        openset = {start:0}
        heapq.heappush(fringe, (0,time.time(),0,start))
        while fringe:
            _,_,g,current = heapq.heappop(fringe)
            if goal(current):
                while current in parent:
                    path.append(current)
                    current = parent[current]
                if goal_impassible:
                    path = path[1:]
                return path

            closed.add(current)
            for neighbor in set(successor(current,(goal if goal_impassible else lambda t: False))) - closed:
                ng = g + cost(current,neighbor)
                if neighbor in openset:
                    if ng < openset[neighbor]:
                        parent[neighbor] = current
                        openset[neighbor] = ng
                else:
                    c = ng + heuristic(neighbor)
                    heapq.heappush(fringe,(c,time.time(),ng,neighbor))
                    parent[neighbor] = current
                    openset[neighbor] = ng

        return []#"No path found"    

    # <<-- Creer-Merge: functions -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
    # if you need additional functions for your AI you can add them here
    def display_map(self):
        """A function to display the current state of the map, mainly used for
            debugging without the visualizer. Use this to see a live view of what
            is happening during a game, but the visualizer should be much clearer
            and more helpful. To use this, make sure to un-comment the import for
            colorama and download it with pip.
        """

        print('\033[0;0H', end='')

        for y in range(0, self.game.map_height):
            print(' ', end='')
            for x in range(0, self.game.map_width):
                t = self.game.tiles[y * self.game.map_width + x]

                if t.machine is not None:
                    if t.machine.ore_type == 'redium':
                        print(Back.RED, end='')
                    else:
                        print(Back.BLUE, end='')
                elif t.is_wall:
                    print(Back.BLACK, end='')
                else:
                    print(Back.WHITE, end='')

                foreground = ' '

                if t.machine is not None:
                    foreground = 'M'

                print(Fore.WHITE, end='')

                if t.unit is not None:
                    if t.unit.owner == self.player:
                        print(Fore.CYAN, end='')
                    else:
                        print(Fore.MAGENTA, end='')

                    foreground = t.unit.job.title[0].upper()
                elif t.blueium > 0 and t.blueium >= t.redium:
                    print(Fore.BLUE, end='')
                    if foreground == ' ':
                        foreground = 'R'
                elif t.redium > 0 and t.redium > t.blueium:
                    print(Fore.RED, end='')
                    if foreground == ' ':
                        foreground = 'R'
                elif t.blueium_ore > 0 and t.blueium_ore >= t.redium_ore:
                    print(Fore.BLUE, end='')
                    if foreground == ' ':
                        foreground = 'O'
                elif t.redium_ore > 0 and t.redium_ore > t.blueium_ore:
                    print(Fore.RED, end='')
                    if foreground == ' ':
                        foreground = 'O'
                elif t.owner is not None:
                    if t.type == 'spawn' or t.type == 'generator':
                        if t.owner == self.player:
                            print(Back.CYAN, end='')
                        else:
                            print(Back.MAGENTA, end='')

                print(foreground + Fore.RESET + Back.RESET, end='')

            if y < 10:
                print(' 0' + str(y))
            else:
                print(' ' + str(y))

        print('\nTurn: ' + str(self.game.current_turn) + ' / '
              + str(self.game.max_turns))
        print(Fore.CYAN + 'Heat: ' + str(self.player.heat)
              + '\tPressure: ' + str(self.player.pressure) + Fore.RESET)
        print(Fore.MAGENTA + 'Heat: ' + str(self.player.opponent.heat)
              + '\tPressure: ' + str(self.player.opponent.pressure) + Fore.RESET)

        return
    # <<-- /Creer-Merge: functions -->>
