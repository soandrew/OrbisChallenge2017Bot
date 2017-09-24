from PythonClientAPI.Game.Enums import Team
from PythonClientAPI.Game import PointUtils
from PythonClientAPI.Game.Entities import FriendlyUnit, EnemyUnit, Tile
from PythonClientAPI.Game.Enums import Direction, MoveType, MoveResult
from PythonClientAPI.Game.World import World

class PlayerAI:
    def __init__(self):
        """
        Any instantiation code goes here
        """
        self.turn_count = 0
        self.targets = {}
        self.uuid_to_target = {}
        self.nest_points = set()
        self.nest_avoid_points = set()

    def do_move(self, world, friendly_units, enemy_units):
        """
        This method will get called every turn.

        :param world: World object reflecting current game state
        :param friendly_units: list of FriendlyUnit objects
        :param enemy_units: list of EnemyUnit objects
        """
        # Build nests and then attack

        # Cache world information used for attacking
        enemy_nest_positions = world.get_enemy_nest_positions();
        enemy_nest_neighbour_positions = sum([list(world.get_neighbours(point).values())
                                                for point in enemy_nest_positions],
                                             [])  # Nested list flatenning
        enemy_positions = {enemy.position for enemy in enemy_units}
        average_enemy_health = sum(enemy.health for enemy in enemy_units)/len(enemy_units)
        friendly_nest_positions = world.get_friendly_nest_positions()
        friendly_score, enemy_score = calculate_score(world.get_friendly_tiles(), world.get_enemy_tiles())

        # First turn initialization
        if self.turn_count == 0:
            first_nest = friendly_nest_positions[0]
            self.nest_points.add(first_nest)
            self.nest_avoid_points |= get_nest_avoid_points_around(first_nest)

        # Loop over friendly units and assign them to build nests or attack
        for i, unit in enumerate(friendly_units):
            # Schedule new nest to build every fourth turn
            if (self.turn_count % 4 == 0
                    and ((i != 0 and i % 4 == 0) or self.turn_count == 0)):
                nest = world.get_closest_neutral_tile_from(unit.position, self.nest_avoid_points)
                if nest:  # FOund a spot to build a nest
                    self.targets = world.get_tiles_around(nest.position)
                    self.nest_points.add(nest.position)
                    self.nest_avoid_points |= get_nest_avoid_points_around(nest.position)
                else:  # No more space for nests
                    self.targets = None

            attack = True  # Boolean flag for whether to attack or defend
            if self.targets:
                # Assign unit a target if not already have one
                if unit.uuid not in self.uuid_to_target:
                    idx = i % 4

                    if idx > (len(self.targets) - 1):
                        self.uuid_to_target[unit.uuid] = [(0, 0), True]
                    else:
                        direction = Direction.ORDERED_DIRECTIONS[idx]
                        while idx < 4 and (direction not in self.targets):
                            direction = Direction.ORDERED_DIRECTIONS[idx]
                            idx += 1

                        if idx == 4:
                            self.uuid_to_target[unit.uuid] = [(0, 0), True]
                        else:
                            self.uuid_to_target[unit.uuid] = [self.targets[direction].position,
                                                              False]
                            attack = False

                # If unit is already in target position
                if self.uuid_to_target[unit.uuid][0] == unit.position:
                    # change bool to True
                    self.uuid_to_target[unit.uuid][1] = True

                # If unit hasn't reached it's target yet
                if not self.uuid_to_target[unit.uuid][1]:
                    # Calculate path for unit to go to target
                    path = world.get_shortest_path(unit.position, self.uuid_to_target[unit.uuid][0], self.nest_points)
                    if path:
                        attack = False
                    else:
                        path = world.get_shortest_path(unit.position, self.uuid_to_target[unit.uuid][0], None)
                        attack = False

            if attack:  # Attack mode
                # Locate enemy units stronger than this unit
                strong_enemy_positions = {enemy.position for enemy in enemy_units
                                           if enemy.health > unit.health}

                # Look at neighbouring points to make best decision
                target = None
                avoid = set()
                for point in world.get_neighbours(unit.position).values():
                    if point in enemy_nest_neighbour_positions and point not in strong_enemy_positions:
                        if len(enemy_nest_positions) == 1 and friendly_score + 10 <= enemy_score - 5:  # Lose if attack
                            avoid.add(point)
                            continue
                        else:
                            target = point
                            break
                    elif point in enemy_positions and point not in strong_enemy_positions:
                        target = point
                        break
                if not target:  # No good targets in neighbouring points
                    # Check if it's smarter to just rest
                    if unit.health < average_enemy_health and unit.position not in friendly_nest_positions:
                        continue
                    # Best decision is to target closest capturable tile
                    target = world.get_closest_capturable_tile_from(unit.position, self.nest_points | avoid).position

                # Get path
                path = world.get_shortest_path(unit.position, target, self.nest_points | avoid)

            if path:
                world.move(unit, path[0])
            i += 1
        self.turn_count += 1



def get_nest_avoid_points_around(point):
    """
    Return the set of points around point, including point, to avoid scheduling a nest on.

    :param (int, int) point: a nest point
    :return: the set of points around point to avoid scheduling a nest on
    :rtype: set of points
    """
    x, y = point[0], point[1]
    return {(x, y - 2),
            (x - 1, y - 1), (x, y - 1), (x + 1, y - 1),
            (x - 2, y), (x - 1, y), point, (x + 1, y), (x + 2, y),
            (x - 1, y + 1), (x, y + 1), (x + 1, y + 1),
            (x, y + 2)}


def calculate_score(friendly_tiles, enemy_tiles):
    """
    Calculate and return the current score.

    :param list of Tile friendly_tiles:
    :param list of Tile enemy_tiles:
    :return: the current score as a tuple (friendly_score, enemy_score)
    :rtype: (int, int)
    """
    friendly_permanent_tiles = [tile for tile in friendly_tiles if tile.is_permanently_owned()]
    enemy_permanent_tiles = [tile for tile in enemy_tiles if tile.is_permanently_owned()]
    num_friendly_permanent_tiles = len(friendly_permanent_tiles)
    num_enemy_permanent_tiles = len(enemy_permanent_tiles)
    num_friendly_non_permanent_tiles = len(friendly_tiles) - num_friendly_permanent_tiles
    num_enemy_non_permanent_tiles = len(enemy_tiles) - num_enemy_permanent_tiles
    return (num_friendly_non_permanent_tiles + 2 * num_friendly_permanent_tiles, num_enemy_non_permanent_tiles + 2 * num_enemy_permanent_tiles)
