import pygame
import pygame_gui

from settings import *
from grid import Grid
from ui import UI

class PerceptronIllustration:
    def __init__(self) -> None:
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('PerceptronIllustration')
        self.clock = pygame.time.Clock()
        self.running = True

        # UI
        self.uiManager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.ui = UI(pygame.Rect((WINDOW_WIDTH - 158, -2), (160, 150)), self.uiManager)

        # Grid
        self.grid = Grid(WINDOW_WIDTH, WINDOW_HEIGHT, ui=self.ui)

        # Start game loop
        self.run()

    def run(self) -> None: 
        while self.running:
            dt = self.clock.tick() / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                self.grid.handle_event(event)

                self.uiManager.process_events(event)
                self.ui.process_event(event)

            # Update
            self.uiManager.update(dt)
            self.grid.update()
            
            # Draw
            self.display_surface.fill("white")
            self.grid.draw()
            self.uiManager.draw_ui(self.display_surface)

            pygame.display.update()

        pygame.quit()


if __name__ == "__main__":
    PerceptronIllustration()