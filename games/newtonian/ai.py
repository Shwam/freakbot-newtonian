# This is where you build your AI for the Newtonian game.

from joueur.base_ai import BaseAI

# <<-- Creer-Merge: imports -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
# you can add additional import(s) here

#from colorama import init, Fore, Back, Style
import heapq
import time

# <<-- /Creer-Merge: imports -->>

enemy = None
    
counters = {"intern":"manager", "physicist":"intern", "manager":"physicist"} # manager is counters[intern]
countered_by = {"manager":"intern", "intern":"physicist", "physicist":"manager"} # intern is countered_by[manager]

def radius(tile, r=1):
    frontier = {tile}
    tiles = set()
    while r >= 0:
        r -= 1
        tiles |= frontier
        if r >= 0:
            for t in frontier:
                frontier = set(t.get_neighbors())
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
        for tile in self.game.tiles:
            if tile.unit and tile.unit.owner != self.player:
                for t in radius(tile, 5):
                    cost[t] += 2/(1+manhattan(t,tile)) * (1 if counters[tile.unit.job.title] == unit.job.title else -1 if countered_by[tile.unit.job.title] == unit.job.title else 0)
                    cost[t] += (tile.unit.health-unit.health)/(1+manhattan(t,tile))
            elif tile.unit and tile.unit != unit:
                for t in radius(tile, 6):
                    cost[t] += -1/(1+manhattan(t,tile))
            if unit.job.title == "physicist":
                if tile.machine:
                    for t in radius(tile, 6):
                        cost[t] -= (unit.redium_ore+unit.blueium_ore)/(1+manhattan(t,tile))/15
            if unit.job.title == "intern":
                if tile.blueium_ore or tile.redium_ore:
                    for t in radius(tile, 6):
                        cost[t] -= (tile.redium_ore*(1+self.player.pressure-self.player.heat)+tile.blueium_ore*(1+self.player.heat-self.player.pressure))/(1+manhattan(t,tile))/15
            if unit.job.title == "manager":
                if tile.blueium or tile.redium or tile.machine:
                    for t in radius(tile, 6):
                        cost[t] -= 3/(1+manhattan(t,tile))
        mx = max(cost.values())
        mn = min(cost.values())

        for tile in cost:
            cost[tile] = (cost[tile] - mn)/(mx-mn)
        return cost

    def free_actions(self, unit):
        if unit.acted:
            return True
        for t in unit.tile.get_neighbors() + [unit.tile]:
            if unit.job.title == 'intern':
                if t.owner != self.player.opponent and t.machine:
                    if unit.blueium_ore > 0 and t.machine.ore_type == "blueium" and unit.drop(t, 0, 'blueium ore'):
                        pass
                    if unit.redium_ore > 0 and t.machine.ore_type == "redium" and unit.drop(t, 0, 'redium ore'):
                        pass
                if not t.machine and unit.blueium_ore + unit.redium_ore < unit.job.carry_limit:
                    if t.blueium_ore > 0 and unit.pickup(t, 0, 'blueium ore'):
                        pass
                    if t.redium_ore > 0 and unit.pickup(t, 0, 'redium ore'):
                        pass
            elif unit.job.title == 'manager':
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
                    

    def act(self, unit, enable_attack=True):
        if unit.acted:
            return True
        self.free_actions(unit)
        if unit.job.title == 'physicist':
            for t in unit.tile.get_neighbors() + [unit.tile]:
                if t.machine and (t.machine.ore_type == "blueium" and t.blueium_ore >= t.machine.refine_input or t.machine.ore_type == "redium" and t.redium_ore >= t.machine.refine_input) and unit.act(t):
                    return True
                if t.unit and t.unit.owner != unit.owner and t.unit.health > 0:
                    if (t.unit.job.title == "manager" and t.unit.stun_time == 0 and t.unit.stun_immune == 0 and unit.act(t)):
                        if unit.acted:
                            return True
                    if (enable_attack and unit.moves >= unit.job.moves and unit.attack(t)):
                        return True
        elif unit.job.title == 'intern':
            for t in unit.tile.get_neighbors() + [unit.tile]:
                if t.unit and t.unit.owner != unit.owner and t.unit.health > 0:
                    if (t.unit.job.title == "physicist" and t.unit.stun_time == 0 and t.unit.stun_immune == 0 and unit.act(t)):
                        if unit.acted:
                            return True
                    if (enable_attack and unit.moves >= unit.job.moves and unit.attack(t)):
                        return True
        elif unit.job.title == 'manager':
            for t in unit.tile.get_neighbors() + [unit.tile]:
                if t.unit and t.unit.owner != unit.owner and t.unit.health > 0:
                    if (t.unit.job.title == "intern" and t.unit.stun_time == 0 and t.unit.stun_immune == 0 and unit.act(t)):
                        if unit.acted:
                            return True
                    if (enable_attack and unit.moves >= unit.job.moves and unit.attack(t)):
                        return True
        return False

    def do_stuff(self, unit):
        if unit is not None and unit.tile is not None and unit.stun_time <= 0 and not unit.acted and unit.moves:
            cost = manhattan
            if self.player.time_remaining > 10**10:
                costs = self.cost_map(unit)
                cost = lambda _,n: costs[n]
            
            if unit.job.title == "manager" and unit.redium or unit.blueium:
                # RUN HOME, DON'T LOOK BACK
                goal = lambda tile: tile in self.player.generator_tiles
                
                path = self.a_star(unit.tile, goal, goal_impassible=False,cost=cost)
                while unit.moves > 0 and path:
                    self.free_actions(unit)
                    if not unit.move(path.pop()):
                        break
                self.free_actions(unit)

            if unit.job.title == "manager" and unit.blueium + unit.redium < unit.job.carry_limit and any(manhattan(unit.tile, tile) <= unit.moves + 1 for tile in self.game.tiles if tile.blueium or tile.redium):
                # Grab it and run
                goal = lambda tile: (tile.blueium or tile.redium)

                path = self.a_star(unit.tile, goal, goal_impassible=False,cost=cost)
                while unit.moves and path:
                    self.free_actions(unit)
                    if not unit.move(path.pop()):
                        break
            
            if unit.job.title == "manager" and unit.redium or unit.blueium:
                # RUN HOME, DON'T LOOK BACK
                goal = lambda tile: tile in self.player.generator_tiles
                
                path = self.a_star(unit.tile, goal, goal_impassible=False,cost=cost)
                while unit.moves > 0 and path:
                    self.free_actions(unit)
                    if not unit.move(path.pop()):
                        break
                self.free_actions(unit)


            if any(manhattan(unit.tile, u2.tile) <= unit.moves + 1 and unit.health == 1 for u2 in self.player.opponent.units if u2.tile and unit.tile):
                goal = lambda tile: tile.unit and tile.unit.owner != self.player and unit.health == 1
                path = self.a_star(unit.tile, goal, cost=cost)
                if len(path) <= unit.moves + 1:
                    while unit.moves and path:
                        if not unit.move(path.pop()):
                            break

            if any(manhattan(unit.tile, u2.tile) <= unit.moves + 1 and counters[u2.job.title] == unit.job.title for u2 in self.player.opponent.units if u2.tile and unit.tile):
                goal = lambda tile: tile.unit and tile.unit.owner != self.player and counters[tile.unit.job.title] == unit.job.title
                path = self.a_star(unit.tile, goal, cost=cost)
                if len(path) <= unit.moves + 1:
                    while unit.moves and path:
                        if not unit.move(path.pop()):
                            break
                    self.act(unit)

            if False and unit.health <= unit.job.health/3 and unit.blueium_ore + unit.redium_ore + unit.blueium + unit.redium <= 0:
                goal = lambda tile: tile.owner == self.player and not tile.unit
                path = self.a_star(unit.tile, goal, goal_impassible=False,cost=cost)

                while unit.moves > 0 and path:
                    if not unit.move(path.pop()):
                        break

            elif unit.job.title == 'physicist':
                goal = lambda tile: tile.machine and tile.blueium_ore + tile.redium_ore >= tile.machine.refine_input
                path = self.a_star(unit.tile, goal, cost=cost)
                # move toward a machine if there's one with unrefined ores
                while unit.moves > 0 and path:
                    if self.act(unit):
                        return True
                    if not unit.move(path.pop()):
                        break
                
                if not any([goal(m.tile) for m in self.game.machines]):
                    # go harass a manager
                    goal = lambda tile: tile.unit and tile.unit.owner != self.player and tile.unit.job.title == "manager"
                    path = self.a_star(unit.tile, goal, cost=cost)
                    while unit.moves > 0 and path:
                        if self.act(unit):
                            return True
                        if not unit.move(path.pop()):
                            break
            
            elif unit.job.title == 'intern':
                if unit.blueium_ore + unit.redium_ore < unit.job.carry_limit:
                    # gather resources
                    goal = lambda tile: tile.blueium_ore+tile.redium_ore > 0 and tile.machine is None
                    path = self.a_star(unit.tile, goal, goal_impassible=False,cost=cost)
                    while unit.moves > 0 and path:
                        if self.act(unit):
                            return True
                        if not unit.move(path.pop()):
                            break
                else:
                    # return to reactor
                    goal = lambda tile: tile.owner != self.player.opponent and tile.machine and (tile.machine.ore_type == "blueium" and unit.blueium_ore > 0 or tile.machine.ore_type == "redium" and unit.redium_ore > 0)
                    path = self.a_star(unit.tile, goal, cost=cost)
                    while unit.moves > 0 and path:
                        if self.act(unit):
                            return True
                        if not unit.move(path.pop()):
                            break
            
            elif unit.job.title == 'manager':
                goal = lambda tile: (tile.blueium or tile.redium)
                if not unit.redium and not unit.blueium and any(goal(t) for t in self.game.tiles):
                    path = self.a_star(unit.tile, goal, goal_impassible=False, cost=cost)
                    while unit.moves > 0 and  path:
                        self.free_actions(unit)
                        if not unit.move(path.pop()):
                            break
                    self.act(unit)
                # harass interns
                goal = lambda tile: tile.unit and tile.unit.owner != self.player and tile.unit.health > 0 and tile.unit.job.title == "intern"
                path = self.a_star(unit.tile, goal, goal_impassible=True,cost=cost)
                while unit.moves > 0 and path:
                    if self.act(unit):
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
        print(self.player.time_remaining/(10**9))
        for unit in self.player.units:
            if self.player.time_remaining < 10**9:
                return True
            self.do_stuff(unit)
        for unit in self.player.units:
            if self.player.time_remaining < 10**9:
                return True
            i = 3 
            while unit.tile and unit.moves and not unit.acted and not unit.stun_time and i:
                i -= 1
                self.do_stuff(unit)
        
        return True
        # <<-- /Creer-Merge: runTurn -->>

    def a_star(self, start, goal, successor=walkable, cost=manhattan, heuristic = lambda x: 0, goal_impassible=True):
        path = []

        goal_tiles = [tile for tile in self.game.tiles if goal(tile)]
        if not goal_tiles:
            return path

        tab = dict()
        def heuristic(t):
            if t not in tab:
                h = min([manhattan(t, t2) for t2 in goal_tiles])
                tab[t] = h
            return tab[t]

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
