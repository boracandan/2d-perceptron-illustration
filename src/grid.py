import pygame
import pygame_gui
from collections import deque

from ui import UI
from settings import *
from algorithm import train_perceptron, train_perceptron_step

class Grid:
    def __init__(self, screenWidth: int, screenHeight: int, ui: UI) -> None:
        self.displaySurface = pygame.display.get_surface()
        self.ui = ui

        self.width = screenWidth
        self.height = screenHeight

        self.scale = 50 # pixels between lines
        self.maxScale, self.minScale, self.defaultScale = 100, 25, 50
        self.scalingMultiplier = 3
        self.unitSize = 1.0 # World units per grid square
        self.origin = pygame.Vector2((int(screenWidth // 2), int(screenHeight // 2)))

        # Position UI
        self.font = pygame.font.Font(filename=None, size=20)
        self.roundDigits = 3

        self.preMousePosition = pygame.Vector2(pygame.mouse.get_pos())

        self.points = []
        self.weights = None
        self.weightDeque = deque(maxlen=5)
        self.lastTrainTime = None

    def world_to_screen(self, *args):
        match args:
            case (pygame.Vector2() as coordinate,):
                screenCoordinate = pygame.Vector2(self.origin.x + coordinate.x / self.unitSize * self.scale, self.origin.y - coordinate.y / self.unitSize * self.scale)
                return screenCoordinate
            case coordinates if all(isinstance(c, pygame.Vector2) for c in coordinates):
                return [self.world_to_screen(c) for c in coordinates]
            case [float() | int() as xCoordinate, "x"]:
                return self.origin.x + xCoordinate / self.unitSize * self.scale
            case [float() | int() as yCoordinate, "y"]:
                return self.origin.y - yCoordinate / self.unitSize * self.scale
            case _:
                raise ValueError("Invalid input to world_to_screen")

    def screen_to_world(self, *args):
        match args:
            case (pygame.Vector2() as coordinate,):
                screenCoordinate = pygame.Vector2((coordinate.x - self.origin.x) / self.scale * self.unitSize, (self.origin.y - coordinate.y) / self.scale * self.unitSize)
                return screenCoordinate
            case coordinates if all(isinstance(c, pygame.Vector2) for c in coordinates):
                return [self.screen_to_world(c) for c in coordinates]
            case [float() | int() as xCoordinate, "x"]:
                return (xCoordinate - self.origin.x) / self.scale * self.unitSize
            case [float() | int() as yCoordinate, "y"]:
                return (self.origin.y - yCoordinate) / self.scale * self.unitSize
            case _:
                raise ValueError("Invalid input to screen_to_world")
            
    def draw_mouse_pos(self) -> None:
        self.mousePosition = self.screen_to_world(pygame.Vector2(pygame.mouse.get_pos()))
        textSurf = self.font.render(f"x: {round(self.mousePosition.x, self.roundDigits)}, y: {round(self.mousePosition.y, self.roundDigits)}", True, Color.BLACK)
        textRect = textSurf.get_frect(topleft = (0, 0))

        self.displaySurface.blit(textSurf, textRect)

    def draw_horizontal_label(self, y: float) -> None:
        coordinate = self.screen_to_world(y, "y")
        label = round(coordinate, self.roundDigits)
        labelStr = str(label)

        font_size = max(int(self.scale * 0.4 - len(labelStr)), 10)  # adjust as needed
        font = pygame.font.Font(filename=None, size=font_size)

        textSurf = font.render(str(label), True, Color.BLACK)
        textRect = textSurf.get_frect(midright = (self.origin.x, y))
        self.displaySurface.blit(textSurf, textRect)

    def draw_vertical_label(self, x: float) -> None:
        coordinate = self.screen_to_world(x, "x")
        label = round(coordinate, self.roundDigits)
        labelStr = str(label)

        font_size = max(int(self.scale * 0.4 - len(labelStr)), 10)  # adjust as needed
        font = pygame.font.Font(filename=None, size=font_size)

        textSurf = font.render(str(label), True, Color.BLACK)
        textRect = textSurf.get_frect(midtop = (x, self.origin.y))
        self.displaySurface.blit(textSurf, textRect)

    def draw_axis(self) -> None:
        # Draw Grid
        for xPos in range(int(self.origin.x) + int(self.scale), self.width, int(self.scale)):
            if xPos >= 0:
                pygame.draw.line(self.displaySurface, Color.GRAY, (xPos, 0), (xPos, self.height))

                self.draw_vertical_label(xPos)

        for xPos in range(int(self.origin.x) - int(self.scale), 0, -int(self.scale)):
            if xPos <= self.width:
                pygame.draw.line(self.displaySurface, Color.GRAY, (xPos, 0), (xPos, self.height))

                self.draw_vertical_label(xPos)

        for yPos in range(int(self.origin.y) + int(self.scale), self.height, int(self.scale)):
            if yPos >= 0:
                pygame.draw.line(self.displaySurface, Color.GRAY, (0, yPos), (self.width, yPos))

                self.draw_horizontal_label(yPos)
        
        for yPos in range(int(self.origin.y) - int(self.scale), 0, -int(self.scale)):
            if yPos <= self.height:
                pygame.draw.line(self.displaySurface, Color.GRAY, (0, yPos), (self.width, yPos))

                self.draw_horizontal_label(yPos)

            
        # Draw Axis Lines
        pygame.draw.line(self.displaySurface, Color.BLACK, (self.origin.x, 0), (self.origin.x, self.height))
        pygame.draw.line(self.displaySurface, Color.BLACK, (0, self.origin.y), (self.width, self.origin.y))

    def draw_points(self) -> None:
        pointColPairs = list(map(lambda pointColPair: (self.world_to_screen(pointColPair[0]), pointColPair[2]), self.points))
        for pointColPair in pointColPairs:
            if 0 < pointColPair[0].y < self.height and 0 < pointColPair[0].x < self.width:
                pygame.draw.circle(surface=self.displaySurface, color=pointColPair[1], center=pointColPair[0], radius=2)

    def draw_perceptron_boundary(self) -> None:
        for i, weights in enumerate(self.weightDeque):
            worldX1 = self.screen_to_world(0, "x")
            worldX2 = self.screen_to_world(self.width, "x")

            worldY1 = -(weights[0] + weights[1] * worldX1) / weights[2]
            worldY2 = -(weights[0] + weights[1] * worldX2) / weights[2]
            
            pygame.draw.aalines(self.displaySurface, getattr(Color, f"BLUE_{i}"), False, [(0, self.world_to_screen(worldY1, "y")), (self.width, self.world_to_screen(worldY2, "y"))])

        
    def update_scale(self) -> None:
        if self.minScale <= self.scale <= self.maxScale:
            return
        self.unitSize *= self.defaultScale / self.maxScale if self.scale > self.maxScale else self.defaultScale / self.minScale
        self.scale = self.defaultScale

    def draw(self) -> None:
        self.draw_axis()
        self.draw_mouse_pos()
        self.draw_points()
        self.draw_perceptron_boundary()
    
    def handle_event(self, event: pygame.Event) -> None:
        if event.type == pygame.MOUSEWHEEL:
            mouseScreen = pygame.Vector2(pygame.mouse.get_pos())
            preMousePosition = self.screen_to_world(mouseScreen)
            self.scale += event.y * self.scalingMultiplier
            self.update_scale()
            newMousePosition = self.screen_to_world(mouseScreen)
            self.adjust_origin(preMousePosition, newMousePosition)

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.ui.trainButton:
                points = [(*coordinates, label) for coordinates, label, _ in self.points]
                self.weightDeque.clear()
                self.weightDeque.append(train_perceptron(points))
            elif event.ui_element == self.ui.animatedTrainButton:
                self.lastTrainTime = 0
                self.train_perceptron_flag = True
                self.weightDeque.clear()

        
    def update(self) -> None:
        mousePressed = pygame.mouse.get_pressed()
        mouseJustPressed = pygame.mouse.get_just_pressed()
        keyPressed = pygame.key.get_pressed()
        if not self.ui.mouseInPanel:
            self.handle_mouse_drag(mousePressed)
            self.handle_mouse_just_pressed(mouseJustPressed)
        self.handle_key_pressed(keyPressed)


         # Continuous perceptron training if a flag is set
        if hasattr(self, "train_perceptron_flag") and self.train_perceptron_flag:
            now = pygame.time.get_ticks()
            if now - self.lastTrainTime >= TRAIN_INTERVAL_MS:
                self.lastTrainTime = now
                points = [(*coordinates, label) for coordinates, label, _ in self.points]
                self.weights, hyperplaneFound = train_perceptron_step(points, self.weights)
                self.weightDeque.append(self.weights)

                if hyperplaneFound:
                    self.train_perceptron_flag = False
                    self.weightDeque = deque([self.weightDeque[-1]], maxlen=5)

    def adjust_origin(self, preMousePos: pygame.Vector2, newMousePos: pygame.Vector2) -> None:
        offset = newMousePos - preMousePos
        pixel_offset = offset / self.unitSize * self.scale
        self.origin += pygame.Vector2(round(pixel_offset.x), -round(pixel_offset.y))

    def handle_mouse_drag(self, mousePressed: list) -> None:
        mousePos = pygame.Vector2(pygame.mouse.get_pos())
        if mousePressed[0]: # Mouse Left Click
            self.origin += mousePos - self.preMousePosition
        self.preMousePosition = mousePos

    def handle_mouse_just_pressed(self, mouseJustPressed: list) -> None:
        if mouseJustPressed[2] and (selectedBtn := self.ui.buttonGroup.activeButton): # Mouse right click when a group is selected
            mousePos = self.screen_to_world(pygame.Vector2(pygame.mouse.get_pos()))
            self.points.append((mousePos, 1, Color.RED) if selectedBtn.text == "Group 1" else (mousePos, -1, Color.PURPLE))

    def handle_key_pressed(self, keyPressed: pygame.key.ScancodeWrapper):
        if keyPressed[pygame.K_r]:
            self.points = []
            self.weights = None
            self.weightDeque.clear()

