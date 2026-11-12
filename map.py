"""
map.py - the game world: two maps drawn as text, plus the code that draws and checks them.

Each map is a list of strings. One character = one tile:
    #  wall (blocked)         ~  water/lava (blocked)     T  tree (blocked)
    .  floor (walkable)       ,  tall grass/rubble (walkable, monsters may attack!)
    F  campfire (heals you)   >  <  portals to the other map
    D  the dragon's lair (boss fight)
    E S H G W  NPC markers (the NPC stands here; you talk by walking into them)
    space = empty void (outside the map, blocked)
The maps are NOT squares: they have curved outlines, houses, rivers, ruins and pillars.
"""
import ui

NPC_SYMBOLS = "ESHGW"

ELDORIA_ROWS = [
    "                                #########################",
    "      ###############           #,,.T.,T.T.TT..,,...,.T.#",
    "   ####.............####        #,,,,.,..#####..,..,..,.#",
    "   #...................#        #...,.,.,#,,,#,,,.....>.#",
    "   #...................~~~     ###T.W..,,#,,,#,,,,,.....#",
    "   #..####.....#####.T.~~~     ##..,.,..,,,,,,,,,,......#",
    "   #..####.....#####...~~~     #T....,,,.TT,,,TT,,,T..,,#",
    "   #..####.....#####...~~~     #,,,....T,,,.,T..,.T....,#",
    "   #........E.....H....~~~######,,,,.,,......,.,TT,,....#",
    "   #.T..........................................G.,,...,#",
    "   #....S..............~~~####,,,,,,,,,.,T.....,,,,,,,,.#",
    "   #..#####.##..####...~~~   #,,,,,,,....T.,#.,,,,,,,,,.#",
    "   #..#####.....####...~~~####,,,,,####.....#..,,,,,,,,.#",
    "   #..#####.~~~.####.T.~~~#T,T...,..,....,..#,..,,#######",
    "   #........~~~........~~~#,.T..T,,,,,..,,T.,,...,#",
    "   #.....T.............#  #,...,,,,,,,,,.T..,..,,.#",
    "   ####.............####  ########,,,,,,,.,#.,,T,T#",
    "      ###############            #..,..,...#.,...,#",
    "                                 ##################",
]

CAVERN_ROWS = [
    "                                    ##############",
    "         ###################        #............#",
    "         #...........,#,...##########....,..~~,,.#",
    "         #....#....,,,,,,,............#,,,,,,,,,,#",
    "         #..F.#......,,,..............#,,,,,,,,,.#",
    "         #.................##########..,,,,,.....#",
    "         ##########..#######        #...#,....#..#",
    "                  #..#              #.........F..#",
    "                  #..#        ##### ######..######",
    "             ######..#####    #,,,#      #..#",
    "             #..~~.......######,,,#      #..#",
    " #########   #..,,,,,..........,,,########..##########",
    " #.......#   #,,,,,,,,,..............................#",
    " #.......#####..,,,,,....#########..............~~...#",
    " #.<.......,.........#####       #..#.............#..#",
    " #.......,,,,,......,####        #..#......D.........#",
    " #.......######..,,,,,,,#        #......#.....#...#..#",
    " #.......#    #.....,...#        #...................#",
    " #########    ###########        #####################",
]


class GameMap:
    def __init__(self, key, title, rows, spawn, monster_pool, encounter_rate, portals, styles=None):
        width = max(len(row) for row in rows)
        self.key = key
        self.title = title
        self.grid = [list(row.ljust(width)) for row in rows]   # grid[y][x]
        self.spawn = spawn                  # (x, y) where you start / respawn
        self.monster_pool = monster_pool    # names; repeats make a monster more common
        self.encounter_rate = encounter_rate
        self.portals = portals              # {symbol: (destination map key, (x, y))}
        self.styles = {
            "#": ui.GREY, "~": ui.BLUE, "T": ui.GREEN, ",": ui.GREEN, ".": ui.WHITE,
            "F": ui.YELLOW, ">": ui.MAGENTA, "<": ui.MAGENTA, "D": ui.RED,
        }
        self.styles.update(styles or {})
        self.markers = {}                   # NPC letter -> (x, y)
        for y, row in enumerate(self.grid):
            for x, char in enumerate(row):
                if char in NPC_SYMBOLS:
                    self.markers[char] = (x, y)
                    self.grid[y][x] = "."   # the floor under the NPC

    @property
    def height(self):
        return len(self.grid)

    @property
    def width(self):
        return len(self.grid[0])

    def in_bounds(self, x, y):
        return 0 <= y < self.height and 0 <= x < self.width

    def tile(self, x, y):
        """The character at (x, y); walls for anything outside the map."""
        return self.grid[y][x] if self.in_bounds(x, y) else "#"

    def is_walkable(self, x, y):
        return self.tile(x, y) in ".,F"

    def npc_at(self, x, y, npcs):
        for npc in npcs:
            if npc.map_key == self.key and self.markers.get(npc.symbol) == (x, y):
                return npc
        return None

    def render(self, player_x, player_y, npcs):
        """Return the whole map as one colored string."""
        npc_positions = {self.markers[n.symbol]: n.symbol for n in npcs
                         if n.map_key == self.key and n.symbol in self.markers}
        lines = []
        for y, row in enumerate(self.grid):
            line = ""
            for x, char in enumerate(row):
                if (x, y) == (player_x, player_y):
                    line += ui.paint("@", ui.YELLOW, True)
                elif (x, y) in npc_positions:
                    line += ui.paint(npc_positions[(x, y)], ui.CYAN, True)
                elif char == " ":
                    line += " "
                else:
                    line += ui.paint(char, self.styles.get(char, ui.WHITE), char in "<>D")
            lines.append(line)
        return "\n".join(lines)


def build_maps():
    eldoria = GameMap(
        "eldoria", "Eldoria Village & Whispering Forest", ELDORIA_ROWS,
        spawn=(10, 9),
        monster_pool=["Slime", "Slime", "Goblin", "Wolf"],
        encounter_rate=0.35,
        portals={">": ("cavern", (4, 14))},
    )
    cavern = GameMap(
        "cavern", "The Ashen Caverns", CAVERN_ROWS,
        spawn=(4, 14),
        monster_pool=["Skeleton", "Skeleton", "Skeleton", "Orc"],
        encounter_rate=0.5,
        portals={"<": ("eldoria", (53, 3))},
        styles={"#": ui.WHITE, "~": ui.RED, ",": ui.YELLOW, ".": ui.GREY},
    )
    return {"eldoria": eldoria, "cavern": cavern}
