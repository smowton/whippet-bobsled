import numpy
import collections
import datatypes.trace as trace
import model_reader.model_functions as model_functions
import bot_locomotion.pathfinding as pathfinding

from enum import Enum

add = trace.coord_add
subtract = trace.coord_subtract

class Mode(Enum):
    WORKER = 1
    INITIALISER = 2
    BUILDER_UP = 3
    BUILDER_DOWN = 4
    IDLER = 5

class Action(Enum):
    MOVE = 1
    FILL = 2
    SPLIT = 3

def in_range(position, range):
    if position[0] < 0 or position[0] >= range[0]:
        return False
    if position[1] < 0 or position[1] >= range[1]:
        return False
    if position[2] < 0 or position[2] >= range[2]:
        return False
    return True

def is_target(coord):
   return (coord[0] * 2 + coord[2]) % 5 == 0

def change_height(position, height):
    return (position[0], height, position[2])

def get_layer_targets(layer, layer_direction):
    targets = dict()
    for point in layer:
        if is_target(point):
            targets[point] = Target(point, layer_direction, layer)
        for direction in model_functions.lateral_directions:
            adjacent_point = add(point, direction)
            if is_target(adjacent_point):
               targets[adjacent_point] = Target(adjacent_point, layer_direction, layer)
    return targets

def get_targets(layers, layer_index = 0, previous_layer_height = -1, previous_layer_targets = dict(), floodfill_depth = 0):
    print 'LAYER', layer_index
    layer = layers[layer_index]
    direction = layer[1] - previous_layer_height
    targets = get_layer_targets(layer[0], direction)
    for target in targets.values():
        target.floodfill_depth = floodfill_depth + (0 if direction == 1 else 10000)
        parent_target_position = change_height(target.position, previous_layer_height)
        if parent_target_position in previous_layer_targets:
            target.parent = previous_layer_targets[parent_target_position]

    child_targets = dict()
    for child_layer_index in layer[2]:
        child_targets.update(get_targets(layers, child_layer_index, layer[1], targets, floodfill_depth + 1))
    targets.update(child_targets)

    return targets

def calculate_max_targets(layers, index = 0):
    target_counts = []
    while True:
        layer = layers[index]
        target_counts.append(len(get_layer_targets(layer[0], 1)))
        if len(layer[2]) == 2:
            target_counts.append(calculate_max_targets(layers, layer[2][0]) + calculate_max_targets(layers, layer[2][1]))
            break
        if len(layer[2]) == 1:
            index = layer[2][0]
        if len(layer[2]) == 0:
            break
    return max(target_counts)

def calculate_initial_seeds_kept(desired_bots, max_height):
    production = 0
    total = 0
    i = 0
    while total + 4 < desired_bots:
        if production <= max_height + 2:
            production += 2
        total += production
        i += 1
    return max(i - 1, 0)

def is_voxel_printable(grid, voxel):
    if grid[voxel[0], voxel[1], voxel[2]]:
        return False
    if voxel[1] == 0:
        return True
    for direction in model_functions.directions:
        adjacent_voxel = add(voxel, direction)
        if grid[adjacent_voxel[0], adjacent_voxel[1], adjacent_voxel[2]]:
            return True
    return False

def get_path_points(position, path):
    points = [position]
    for vector in path:
        direction = trace.direction_vector(vector)
        for i in range(trace.l1norm(vector)):
            position = add(position, direction)
            points.append(position)
    return points

class World:
    def __init__(self, model, total_bots):
        self.commands = []
        self.model = model
        self.bounds = model_functions.outer_bounds(self.model)
        self.state = numpy.zeros(self.model.shape, bool)
        self.volatile = set()
        self.bots = collections.OrderedDict([
            ((0, 0, 0), Bot(0, Mode.INITIALISER, (0, 0, 0), range(1, total_bots), self))
        ])

        print 'GETTING LAYERS'
        self.layers = model_functions.get_floodfill_layers(self.model)
        print 'GETTING TARGETS'
        self.targets = get_targets(self.layers)

        self.desired_bots = min(total_bots, calculate_max_targets(self.layers))
        self.desired_bots = 20
        self.initial_seeds_kept = calculate_initial_seeds_kept(self.desired_bots, self.model.shape[1])

        self.is_occupied_state = lambda position: self.is_occupied(position, check_bots = False)
        self.is_occupied_bots = lambda position: self.is_occupied(position, check_bots = True)

        self.step = 0

    def find_target(self, position, active):
        targets = self.active_targets if active else self.inactive_targets
        sorted_targets = sorted([target for target in targets if not target.reserved], key=lambda target: trace.l1norm(subtract(target.get_worker_position(), position)))
        sorted_targets = sorted(sorted_targets, key=lambda target: target.floodfill_depth)
        return next(iter(sorted_targets), None)

    def update_targets(self):
        self.active_targets = [target for target in self.targets.values() if target.is_ready(self.state, self.bots)]
        self.inactive_targets = [target for target in self.targets.values() if not target.is_ready(self.state, self.bots) and not target.is_finished()]

    def is_occupied(self, position, check_bots = False, check_volatile = False):
        if not in_range(position, self.model.shape):
            return True
        if self.state[position[0], position[1], position[2]]:
            return True
        if check_bots and position in self.bots:
            return True
        if check_volatile and position in self.volatile:
            return True
        return False

    def update_bot_position(self, old_position, new_position):
        bot = self.bots[old_position]
        del self.bots[old_position]
        self.bots[new_position] = bot

    def next_step(self):
        self.update_targets()

        self.volatile = set()
        self.bots = collections.OrderedDict(sorted(self.bots.items(), key=lambda bot: bot[1].id))

        commands = []
        for bot in self.bots.values():
            print bot.id
            commands.append(bot.next_step())
        self.commands += commands

        if len([True for command in commands if isinstance(command, trace.Trace.Wait)]) == len(commands):
            print 'FINISH BY IDLE', len(self.active_targets), len(self.inactive_targets)
            for bot in self.bots.values():
                print 'BOT', bot, bot.queue
                if bot.target:
                    print 'TARGET', bot.target.get_worker_position(),  bot.target.get_voxels()
            return False

        self.step += 1
        return True

class Target:
    def __init__(self, position, direction, layer):
        self.position = position
        self.direction = direction
        self.layer = layer
        self.voxels = self.get_voxels()
        self.printed_voxels = 0
        self.reserved = False
        self.parent = None

    def is_occupied_by_worker(self, bots):
        return self.get_worker_position() in bots

    def is_ready(self, grid, bots):
        return not self.reserved and not self.is_occupied_by_worker(bots) and self.get_printable_voxel(grid) and not self.is_finished() and self.is_parent_finished()

    def is_parent_finished(self):
        return not self.parent or self.parent.is_finished()

    def is_finished(self):
        return len(self.voxels) == self.printed_voxels

    def get_printable_voxel(self, grid):
        if self.is_parent_finished():
            for voxel in self.voxels:
                if is_voxel_printable(grid, voxel):
                    return voxel
        return None

    def get_voxels(self):
        voxels = set()
        for point in self.layer:
            if point == self.position:
                voxels.add(self.position)
            for direction in model_functions.lateral_directions:
                adjacent_point = add(self.position, direction)
                if adjacent_point == point:
                    voxels.add(adjacent_point)
        return voxels

    def get_worker_position(self):
        return add(self.position, (0, self.direction, 0))

class Bot:
    def __init__(self, id, mode, position, seeds, world, parent = None):
        self.id = id
        self.mode = mode
        self.position = position
        self.seeds = seeds
        self.world = world
        self.parent = parent
        self.queue = []
        self.counter = 0
        self.target = None

    def __repr__(self):
        return "Bot #{0}, position: {1}, len(seeds): {2}".format(self.id, self.position, len(self.seeds))

    def is_idle(self):
        return len(self.queue) == 0

    def can_move(self, path_points):
        for point in path_points[1:]:
            if (self.world.is_occupied(point, check_bots = True, check_volatile = True)):
                return False
        return True

    def set_mode(self, mode):
        self.mode = mode
        self.counter = 0

    def next_step(self):
        if len(self.queue) > 0:
            action = self.queue.pop(0)
            if action[0] == Action.MOVE:
                command, action = self.move_step(action[1:])
                if (action):
                    self.queue.append(action)
                return command

            if action[0] == Action.FILL:
                command, action = self.fill_step(action[1:])
                if (action):
                    self.queue.append(action)
                return command

            if action[0] == Action.SPLIT:
                command, action = self.split_step(action[1:])
                if (action):
                    self.queue.append(action)
                return command

        counter = self.counter
        self.counter += 1

        if self.mode == Mode.INITIALISER:
            if len(self.world.bots) < self.world.desired_bots:
                center = (self.world.model.shape[1] / 2, self.world.model.shape[2] / 2)
                if counter == 0:
                    return self.move((0, center[0], center[1]))
                elif counter == 1:
                    command = self.split(Mode.BUILDER_UP, (0, 1, 0), (len(self.seeds) - 1) / 2)
                    self.set_mode(Mode.BUILDER_DOWN)
                    return command

            self.set_mode(Mode.WORKER)
            return self.next_step()

        if self.mode == Mode.BUILDER_UP:
            if len(self.world.bots) < self.world.desired_bots:
                if counter == 0 and len(self.seeds) > 2:
                    if not self.parent or self.parent == Mode.BUILDER_DOWN:
                        seeds_kept = self.world.initial_seeds_kept
                    else:
                        seeds_kept = len(self.parent.seeds)
                    return self.split(Mode.BUILDER_UP, (0, 1, 0), len(self.seeds) - seeds_kept - 1)
                elif len(self.seeds) > 0:
                    return self.split(Mode.WORKER, (0, 0, 1 if counter % 2 == 0 else -1), 0)

            self.set_mode(Mode.WORKER)
            return self.next_step()

        if self.mode == Mode.BUILDER_DOWN:
            if len(self.world.bots) < self.world.desired_bots:
                if counter == 0 and len(self.seeds) > 2:
                    if not self.parent or self.parent == Mode.BUILDER_UP:
                        seeds_kept = self.world.initial_seeds_kept
                    else:
                        seeds_kept = len(self.parent.seeds)
                    return self.split(Mode.BUILDER_DOWN, (0, -1, 0), len(self.seeds) - seeds_kept - 1)
                elif len(self.seeds) > 0:
                    return self.split(Mode.WORKER, (0, 0, 1 if counter % 2 == 0 else -1), 0)

            self.set_mode(Mode.WORKER)
            return self.next_step()

        if self.mode == Mode.WORKER:
            if self.target:
                if self.target.is_finished():
                    self.target.reserved = False
                    self.target = None
                    print self.id, 'TARGET DONE'
                    return self.next_step()

                if self.position != self.target.get_worker_position():
                    print self.id, 'MOVING TO TARGET'
                    print self.position, self.target.get_worker_position()
                    return self.move(self.target.get_worker_position())

                # if not self.target.is_ready(self.world.state, self.world.bots):
                #     self.target.reserved = False
                #     self.target = None
                #     print self.id, 'TARGET END'
                #     return self.idle()

                voxel = self.target.get_printable_voxel(self.world.state)
                if voxel:
                    self.target.printed_voxels += 1
                    print self.id, 'FILLING'
                    return self.fill(voxel)

                print self.id, 'IDLE CANT PRINT'
                return self.idle()

            else:
                target = self.world.find_target(self.position, True) or self.world.find_target(self.position, False)
                if target:
                    self.target = target
                    target.reserved = True
                    print self.id, 'TARGET CHOSEN'
                    return  self.next_step()
                print self.id, 'NO TARGET, MOVING AWAY'
                self.mode = Mode.IDLER
                return self.next_step()

        if self.mode == Mode.IDLER:
            idle_position = (0, self.id / 10, self.id % 10)
            if self.position != idle_position:
                return self.move(idle_position)
            return self.idle()

        raise Exception('Bot had no valid next step')

    def idle(self):
        return trace.Trace.Wait(self.id)

    def move(self, goal):
        self.queue.append((Action.MOVE, goal, None))
        return self.next_step()

    def fill(self, voxel):
        self.queue.append((Action.FILL, voxel))
        return self.next_step()

    def split(self, mode, direction, seeds):
        self.queue.append((Action.SPLIT, mode, direction, seeds))
        return self.next_step()

    def split_step(self, action):
        mode, direction, seeds = action

        position = add(self.position, direction)
        if self.world.is_occupied(position, check_bots = True, check_volatile = True):
            return (self.idle(), (Action.SPLIT, mode, direction, seeds))

        new_bot_id = self.seeds[0]
        seeds_given = self.seeds[1:seeds + 1]
        command = trace.Trace.Fission(direction, seeds, self.id, new_bot_id)
        new_bot = Bot(new_bot_id, mode, add(self.position, direction), seeds_given, self.world, self)
        self.world.bots[new_bot.position] = new_bot
        self.seeds = self.seeds[seeds + 1:]
        return (command, None)

    def fill_step(self, action):
        voxel = action[0]
        if self.world.is_occupied(voxel, check_bots = True, check_volatile = True):
            return (self.idle(), (Action.FILL, voxel))

        self.world.state[voxel[0], voxel[1], voxel[2]] = True
        command = trace.Trace.Fill(subtract(voxel, self.position), bot_id = self.id)
        return (command, None)

    def move_step(self, action):
        goal, commands = action

        if goal == self.position:
            raise Exception('Move step when already at goal')

        if commands:
            path_points = get_path_points(self.position, commands[0].get_path())
            if not self.can_move(path_points):
                commands = None

        if not commands:
            path = pathfinding.quick_overhead_search(self.position, goal, self.world.is_occupied_bots)
            # if not path:
            #     path = pathfinding.quick_overhead_search(self.position, goal, self.world.is_occupied_state)
            if not path:
                print '!PATHFINDING!', self.position, goal
                path = pathfinding.bounded_search(self.position, goal, self.world.model.shape, self.world.is_occupied_bots, self.world.bounds)
            if not path:
                print self.id, 'IDLE, NO PATH'
                return (self.idle(), (Action.MOVE, goal, None))
            commands = pathfinding.path_to_commands(path, self.id)

        if commands:
            path_points = get_path_points(self.position, commands[0].get_path())
            if self.can_move(path_points):
                new_position = add(self.position, commands[0].get_distance())
                self.world.update_bot_position(self.position, new_position)
                self.position = new_position
                self.world.volatile.update(path_points)
                action = (Action.MOVE, goal, commands[1:]) if len(commands) > 1 else None
                return (commands[0], action)
            else:
                print self.id, 'IDLE, UNEXPECTED OBSTRUCTION'
                return (self.idle(), (Action.MOVE, goal, commands))
        else:
            print self.id, 'IDLE, KNOWN OBSTRUCTION'
            return (self.idle(), (Action.MOVE, goal, commands))

def build_trace(model, total_bots = 40):
    world = World(model, total_bots)

    while world.next_step():
        pass

    # for c in world.commands:
    #     print c

    return world.commands
