from tkinter import *
import random
from easygui import *
import math
from itertools import product
from random import sample
from matplotlib import pyplot as plt

# Open Menu Gui
while True:
    text = "Please enter attributes"
    title = 'Cellular Automata in Corona Virus'
    input_list = ["Total creatures in simulation (no more than 40,000)", "% of sick creatures",
                  "% of fast moving creatures", "generations until recovery (sick becomes immune)"]
    # list of default text
    default_attributes_list = [15000, 1, 30, 4]
    # creating a integer box
    output = multenterbox(text, title, input_list, default_attributes_list)
    if int(float(output[0])) <= 40000 and 0 <= int(float(output[1])) <= 100 and 0 <= int(float(output[2])) <= 100:
        break

# Corona Virus attributes - confirmed by the user
N = int(float(output[0]))  # number of total creatures in simulation, won't change
D = int(float(output[1]))  # % of Sick creatures, will be updated each generation
R = int(float(output[2]))  # % of fast moving creatures, won't change
X = int(float(output[3]))  # number of generations until sick becomes immune, will be updated each generation
# Corona Virus attributes - constant by default - human behavior
T = 20  # percentage illness threshold (in relation to D)
P_HIGH = 0.6  # if D <= T  ("People are more careful about wearing masks and basic hygiene")
P_LOW = 0.2  # if D > T    ("People are less careful about wearing masks and basic hygiene")

# data structures for later data analysis
infected_population = []
infected_percentage = []
current_generation = 0
generations = []

# Canvas attributes
MATRIX_SIZE = 200
CELL_SIZE = 5
CELLS_ID_LIST = []

# Canvas initiate
display = Tk()
display.title('Cellular Automata in Corona Virus               '
              '                            BLUE = healthy              RED = sick              GREEN = immune')

canvas_frame = Frame(display)
canvas = Canvas(display, bd=0, height=MATRIX_SIZE * CELL_SIZE, width=MATRIX_SIZE * CELL_SIZE)

# define background color
canvas.config(bg='white')
# tell tkinter to fill the display window with the canvas
canvas.pack(expand=True)
# Creature speed attributes
NORMAL, FAST = 1, random.randint(10, 10)

# Creature health_status attributes: HEALTHY(green) -> SICK(red) -> IMMUNE(blue)
EMPTY, HEALTHY, SICK, IMMUNE = 0, 1, 2, 3
EMPTY_COLOR = "white"  # will be used to color empty matrix cells
HEALTHY_COLOR = "blue"
SICK_COLOR = "red"
IMMUNE_COLOR = "green"
CELL_COLOR_LIST = [EMPTY_COLOR, HEALTHY_COLOR, SICK_COLOR, IMMUNE_COLOR]


# Creature Constructor
class Creature:
    def __init__(self, health_status, x_Coordinate, y_Coordinate, speed, remaining_sick_days=X):
        # in the start can be HEALTHY(=1) or SICK(=2)
        self.health_status = health_status
        self.x_Coordinate = x_Coordinate
        self.y_Coordinate = y_Coordinate
        self.speed = speed  # normal or fast(=10 steps per frame)
        self.remaining_sick_days = remaining_sick_days


def Paint_canvas(cell_matrix):
    for row in range(MATRIX_SIZE):
        for column in range(MATRIX_SIZE):
            # first param gets the specific rectangle id,the second param finds the corresponding color
            canvas.itemconfig(CELLS_ID_LIST[row][column], fill=CELL_COLOR_LIST[cell_matrix[row][column]])


def createCreatures():  # creatures will be initialized according to the user input
    creatures = []

    # random coordinates without same indexes
    randomCoordinatesIndexes = sample(list(product(range(200), repeat=2)), k=N)  # create random unique tuples
    sickCreaturesIndexes = [x for x in random.sample([x for x in range(N)], math.ceil((D / 100) * N))]
    fastCreaturesIndexes = [x for x in random.sample([x for x in range(N)], math.ceil((R / 100) * N))]

    for creatureNum in range(N):
        if creatureNum in sickCreaturesIndexes:
            creatureSickOrHealthY = SICK
        else:
            creatureSickOrHealthY = HEALTHY
        if creatureNum in fastCreaturesIndexes:
            creatureFastOrNormal = FAST
        else:
            creatureFastOrNormal = NORMAL
        x_Coordinate = randomCoordinatesIndexes[creatureNum][0]
        y_Coordinate = randomCoordinatesIndexes[creatureNum][1]

        newCreature = Creature(creatureSickOrHealthY, x_Coordinate, y_Coordinate, creatureFastOrNormal, X)
        creatures.append(newCreature)

    return creatures


def buildMatrixFromCreatures(creatures):
    cell_matrix = [[0 for row in range(MATRIX_SIZE)] for column in range(MATRIX_SIZE)]
    for creature in creatures:
        cell_matrix[creature.x_Coordinate][creature.y_Coordinate] = creature.health_status
    return cell_matrix


def create_matrix_grid():
    for x_coordinate in range(MATRIX_SIZE):
        cells_row = []
        for y_coordinate in range(MATRIX_SIZE):
            cell_starting_x = x_coordinate * CELL_SIZE
            cell_starting_y = y_coordinate * CELL_SIZE + CELL_SIZE
            cell_ending_x = x_coordinate * CELL_SIZE + CELL_SIZE
            cell_ending_y = y_coordinate * CELL_SIZE
            # save the rectangles id for future coloring. adds to row
            cells_row.append(
                canvas.create_rectangle(
                    cell_starting_x,
                    cell_starting_y,
                    cell_ending_x,
                    cell_ending_y,
                    fill='white',
                    outline='black'
                )
            )
        # save the rectangles id for future coloring. adds the row to the matrix
        CELLS_ID_LIST.append(cells_row)


def Draw(creatures):
    cell_matrix_with_creatures = buildMatrixFromCreatures(creatures)  # build Matrix From Creatures
    Paint_canvas(cell_matrix_with_creatures)  # paint the creatures on the canvas
    display.update()  # update the display window itself


def update_infected_population(creatures):
    global D, infected_population, current_generation, generations, infected_percentage

    generations.append(current_generation)
    current_generation += 1

    sick_counter = 0
    for creature in creatures:
        if creature.health_status == 2:
            sick_counter += 1
    infected_population.append(sick_counter)
    infected_percentage.append(D)

    D = math.ceil((sick_counter / N) * 100)  # update global variable D
    # print("current % of sick people is: ", D)


def infect_creatures(creatures):
    global D  # taking the most updated % of sick people
    if D <= T:  # % of sick creatures is lower than threshold at the moment
        P = P_HIGH  # people "not putting masks" more chance to get infected
    else:
        P = P_LOW  # people "putting masks" less chance to get infected

    # build data structures to work with
    sick_locations = []  # sick creatures location
    healthy_locations = {}  # healthy creatures location dictionary
    for creature in creatures:
        location = (creature.x_Coordinate, creature.y_Coordinate)  # location tuple (x,y)
        if creature.health_status == SICK:
            sick_locations.append(location)
        else:
            if creature.health_status != 3:
                healthy_locations[location] = creature  # the key will be the location, the value will be the creature
    # check neighbors of sick creatures
    for location in sick_locations:
        x, y = location[0], location[1]
        neighbors = [(x, y + 1), (x, y - 1), (x + 1, y), (x - 1, y), (x - 1, y - 1), (x - 1, y + 1), (x + 1, y - 1),
                     (x + 1, y + 1)]
        for neighbor in neighbors:
            if neighbor in healthy_locations and random.random() < P:
                healthy_locations[neighbor].health_status = SICK  # this neighbor is infected (SICK == 2)

    updateSicknessAndImmunity(creatures)
    update_infected_population(creatures)
    return creatures


def updateSicknessAndImmunity(creatures):
    for creature in creatures:
        if creature.health_status == SICK and creature.remaining_sick_days > 0:  # sick
            creature.remaining_sick_days = creature.remaining_sick_days - 1
            if creature.remaining_sick_days == 0:
                creature.health_status = IMMUNE  # creature is now immune


def move_creatures(creatures):
    creature_locations = {}  # key is a location tuple (x,y) : value is a neighbors list
    for creature in creatures:
        x, y = creature.x_Coordinate, creature.y_Coordinate
        location = (x, y)  # location tuple (x,y)
        s = creature.speed
        m = MATRIX_SIZE
        neighbors = [(x, (y + s) % m), (x, (y - s) % m),
                     ((x + s) % m, y), ((x - s) % m, y),
                     ((x - s) % m, (y - s) % m), ((x - s) % m, (y + s) % m),
                     ((x + s) % m, (y - s) % m), ((x + s) % m, (y + s) % m)]
        creature_locations[location] = neighbors

    for creature in creatures:
        x, y = creature.x_Coordinate, creature.y_Coordinate
        location = (x, y)  # location tuple (x,y)
        if random.random() < (1 / 9):  # stay in (x,y) with some % . go to next creature if chosen
            continue
        # check other movement options
        random.shuffle(creature_locations[location])  # randomize the neighbors
        for neighbor in creature_locations[location]:  # check each neighbor based on open spot
            if neighbor not in creature_locations.keys():
                del creature_locations[(x, y)]  # remove the the location before moving him to the new location
                creature.x_Coordinate = neighbor[0]  # assign a new x coordinate
                creature.y_Coordinate = neighbor[1]  # assign a new y coordinate
                location = (neighbor[0], neighbor[1])  # assign a new location
                creature_locations[location] = 'relocated'  # add the NEW updated location to the location list
                # this creature has been relocated,so we move on to the next creature
                # this location will be now seen as occupied to the following creatures
                break
        # if the creature only possible movement is to stay in (x,y),
        # getting here means the loop didn't break so no need to change anything
    return creatures


if __name__ == "__main__":
    CREATURES = createCreatures()  # initialize creatures list for the entire simulation
    create_matrix_grid()
    Draw(CREATURES)
    while D > 0:  # we run the simulation until all the population is healthy or immune
        CREATURES = infect_creatures(CREATURES)
        CREATURES = move_creatures(CREATURES)
        Draw(CREATURES)

    # this plot will represent the different infection waves of the Corona Virus in the given population
    plt.plot(generations, infected_percentage)
    plt.xlabel('number of generations')
    plt.ylabel('infected population %')
    plt.title('Behavior of Corona Virus epidemic waves ')
    plt.show()

