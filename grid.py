import pygame
import pygame_gui

from ui import UI
from settings import *

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
        self.funcCoef = []

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
        pointWorldCoordinates = list(map(self.world_to_screen, self.points))
        for pointCoordinate in pointWorldCoordinates:
            if 0 < pointCoordinate.y < self.height and 0 < pointCoordinate.x < self.width:
                pygame.draw.circle(self.displaySurface, Color.PURPLE, pointCoordinate, 2)

    def draw_func(self) -> None:
        if self.funcCoef:
            points = []

            for xPixel in range(0, self.width):
                xVal = self.screen_to_world(xPixel, "x")
                yVal = 0
                for i in range(len(self.funcCoef)):
                    yVal += self.funcCoef[i] * xVal ** i

                screenPoint = pygame.Vector2(xPixel, self.world_to_screen(yVal, "y"))
                points.append(screenPoint)

            if len(points) >= 2:
                pygame.draw.aalines(self.displaySurface, Color.BLUE, False, points)

    def update_scale(self) -> None:
        if self.minScale <= self.scale <= self.maxScale:
            return
        self.unitSize *= self.defaultScale / self.maxScale if self.scale > self.maxScale else self.defaultScale / self.minScale
        self.scale = self.defaultScale

    def draw(self) -> None:
        self.draw_axis()
        self.draw_mouse_pos()
        self.draw_points()
        self.draw_func()
    
    def handle_event(self, event: pygame.Event) -> None:
        if event.type == pygame.MOUSEWHEEL:
            mouseScreen = pygame.Vector2(pygame.mouse.get_pos())
            preMousePosition = self.screen_to_world(mouseScreen)
            self.scale += event.y * self.scalingMultiplier
            self.update_scale()
            newMousePosition = self.screen_to_world(mouseScreen)
            self.adjust_origin(preMousePosition, newMousePosition)

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            try:
                pass
            except ValueError:
                pass # silently ignore invalid input

        
    def update(self) -> None:
        mousePressed = pygame.mouse.get_pressed()
        mouseJustPressed = pygame.mouse.get_just_pressed()
        keyPressed = pygame.key.get_pressed()
        if not self.ui.mouseInPanel:
            self.handle_mouse_drag(mousePressed)
            self.handle_mouse_just_pressed(mouseJustPressed)
        self.handle_key_pressed(keyPressed)

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
        if mouseJustPressed[2]: # Mouse Right Click
            mousePos = self.screen_to_world(pygame.Vector2(pygame.mouse.get_pos()))
            self.points.append(mousePos)

    def handle_key_pressed(self, keyPressed: pygame.key.ScancodeWrapper):
        if keyPressed[pygame.K_r]:
            self.points = []

