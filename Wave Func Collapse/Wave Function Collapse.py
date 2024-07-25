import pygame, os, glob
from time import time
from random import choice as random

# I sowwy

pygame.init()

window = pygame.display.set_mode((1000, 1000), pygame.DOUBLEBUF)
pygame.display.set_caption("Wave Function Collapse")

Dir = input("What's the folder name (in the tilesets folder)? ")

pygame.display.set_icon(pygame.image.load("Data/Icon/icon.png"))

def drawImg(Img, Pos):
    x, y = Pos
    x *= PPC
    y *= PPC
    Img = pygame.transform.scale(Img, (1000/DIM,1000/DIM))
    window.blit(Img, (x,y))

def checkValid(arr, valid):
    # Next line means for (int i = arr.length - 1; i >= 0; i--){
    for i in range(len(arr) - 1, -1, -1):
        # Next line means if (!valid.includes(element)){ (element = arr[i])
        if arr[i] not in valid:
            arr.pop(i)

def compareEdge(a, b):
    return a == b[::-1]

class AddGridClass:
    def __init__(self, options, collapsed=False):
        self.collapsed = collapsed
        self.options = list(range(options))
    def __repr__(self):
        return f"Cell({self.collapsed}, {self.options})"

class Tile:
    def __init__(self, img, edges):
        self.img = img
        self.edges = edges

        self.up = []
        self.right = []
        self.down = []
        self.left = []
        
    def __repr__(self):
        return f"Tile({self.img},{self.edges})"
    
    def rotate(self, num):
        img = self.img
        edges = self.edges
            
        newImg = pygame.transform.rotate(img, num*-90)

        newEdges = []
        for i in range(len(edges)):
            newEdges.append([])
            newEdges[i] = edges[(i - num + len(edges)) % len(edges)]

        return Tile(newImg, newEdges)
    
    def analyze(self, tiles):
        # Connection for up
        for i in range(len(tiles)):
            tile = tiles[i]
            if compareEdge(tile.edges[2], self.edges[0]):
                self.up.append(i)
            if compareEdge(tile.edges[3], self.edges[1]):
                self.right.append(i)
            if compareEdge(tile.edges[0], self.edges[2]):
                self.down.append(i)
            if compareEdge(tile.edges[1], self.edges[3]):
                self.left.append(i)

tiles = []
tileImgs = []
rotations = []
grid = []
run = True
Done = False
DIM = 50 # Dimensions of grid
PPC = 1000/DIM # Pixels per cell

for i in range(len(glob.glob(f"Data/Tilesets/{Dir}/*.png"))):
    tileImgs.append(pygame.image.load(f"Data/Tilesets/{Dir}/{i}.png"))

with open (f"Data/Tilesets/{Dir}/rules.txt", "r") as myfile:
    data = myfile.read().splitlines()

for j in range(len(data)):
    tiles.append(Tile(tileImgs[j], list(filter(lambda x: x.isalpha(), [data[j][i:i+3] for i in range(0, len(data[j]), 3)]))))
    rotations.append(int(''.join(filter(lambda x: x.isdigit(), [data[j][i:i+3] for i in range(0, len(data[j]), 3)]))))

for i in range(len(tiles)):
    tile = tiles[i]
    for j in range(1,rotations[i]+1):
        tiles.append(tile.rotate(j))

# Generate Rules & Tiles
for i in range(len(tiles)):
    tile = tiles[i]
    tile.analyze(tiles)
    tiles[i] = tile

for i in range(DIM*DIM):
    grid.append(AddGridClass(len(tiles)))

print("\nStarted!")
pt = 0 # prevTime

while run:
    t = time() #time
    pygame.display.set_caption(f"Wave Function Collapse - {round(1/(t-pt))}FPS")
    pt = time()
    
    window.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    gridCopy = grid[:]
    # List with least amount of options to most.
    # Then filter for the one[s] with the smallest amount of options that aren't collapsed
    gridCopy.sort(key=lambda x: len(x.options))
    gridCopy = [cell for cell in gridCopy if not cell.collapsed]
    gridCopy = [i for i in gridCopy if len(i.options) == min(len(j.options) for j in gridCopy)]

    # If there is more than 2 options to choose from, choose randomly, and collapse it
    try:
        cell = random(gridCopy)
    except:
        if not Done:
            print("Done!")
            Done = True
    
    cell.collapsed = True
    try:
        cell.options = [random(cell.options)]
    except:
        print("Not valid, restart.")
        grid = []
        for i in range(DIM*DIM):
            grid.append(AddGridClass(len(tiles)))
    
    for j in range(DIM):
        for i in range(DIM):
            cell = grid[i + j * DIM]
            if cell.collapsed:
                index = cell.options[0]
                drawImg(tiles[index].img, (i,j))

    nextGrid = []
    for j in range(DIM):
        for i in range(DIM):
            nextGrid.append([])
            index = i + j * DIM
            if grid[index].collapsed:
                nextGrid[index] = grid[index]
            else:
                options = list(range(len(tiles)))

                # Up
                if j > 0:
                    up = grid[i + (j - 1) * DIM]
                    validOptions = []
                    for option in up.options:
                        valid = tiles[option].down
                        validOptions += valid
                    checkValid(options, validOptions)
                    
                # Right
                if i < DIM - 1:
                    right = grid[i + 1 + j * DIM]
                    validOptions = []
                    for option in right.options:
                        valid = tiles[option].left
                        validOptions += valid
                    checkValid(options, validOptions)
                
                # Down
                if j < DIM - 1:
                    down = grid[i + (j + 1) * DIM]
                    validOptions = []
                    for option in down.options:
                        valid = tiles[option].up
                        validOptions += valid
                    checkValid(options, validOptions)
                
                # Left
                if i > 0:
                    left = grid[i - 1 + j * DIM]
                    validOptions = []
                    for option in left.options:
                        valid = tiles[option].right
                        validOptions += valid
                    checkValid(options, validOptions)

                nextGrid[index] = AddGridClass(len(tiles))
                nextGrid[index].options = options
    
    grid = nextGrid
    
    pygame.display.update()

pygame.quit()
