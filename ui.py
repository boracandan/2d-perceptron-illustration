import pygame_gui
import pygame

from settings import *

class UIButton(pygame_gui.elements.UIButton):
    def __init__(self, relative_rect, text, manager = None, container = None, tool_tip_text = None, starting_height = 1, parent_element = None, object_id = None, anchors = None, allow_double_clicks = False, generate_click_events_from = (1,), visible = 1, *, command = None, tool_tip_object_id = None, text_kwargs = None, tool_tip_text_kwargs = None, max_dynamic_width = None, toggle_button = False, brighten_amount=40) -> None:
        super().__init__(relative_rect, text, manager, container, tool_tip_text, starting_height, parent_element, object_id, anchors, allow_double_clicks, generate_click_events_from, visible, command=command, tool_tip_object_id=tool_tip_object_id, text_kwargs=text_kwargs, tool_tip_text_kwargs=tool_tip_text_kwargs, max_dynamic_width=max_dynamic_width)
        self._toggleButton = toggle_button
        self._toggled = False
        self._tint_off = self.colours['normal_bg']

        # Brighten directly in __init__
        c = self._tint_off
        r = min(c.r + brighten_amount, 255)
        g = min(c.g + brighten_amount, 255)
        b = min(c.b + brighten_amount, 255)
        self._tint_on = pygame.Color(r, g, b)

    @property
    def toggled(self) -> bool:
        return self._toggled
    
    def toggle(self) -> None:
        if not self._toggleButton:
            return
        self._toggled = not self.toggled
        self.colours['normal_bg'] = self._tint_on if self._toggled else self._tint_off
        self.rebuild()

   
class ToggleButtonGroup:
    def __init__(self, buttons: list[UIButton]) -> None:
        self.buttons = buttons

    def process_event(self, event: pygame.Event) -> None:
        if (
            event.type == pygame.USEREVENT and
            event.user_type == pygame_gui.UI_BUTTON_PRESSED and
            event.ui_element in self.buttons
        ):
            pressed_button = event.ui_element
            # Toggle pressed button ON
            pressed_button.toggle()
            # Toggle others OFF
            for btn in self.buttons:
                if btn != pressed_button and btn.toggled:
                    btn.toggle()

    @property
    def activeButton(self) -> UIButton | None:
        for btn in self.buttons:
            if btn.toggled: return btn
        return None


class UI:
    def __init__(self, rect: pygame.Rect, manager: pygame_gui.UIManager) -> None:
        # --- Simple Regress UI Panel ---
        self.width, self.height = rect.width, rect.height

        self.uiPanel = pygame_gui.elements.UIPanel(
            relative_rect=rect, 
            manager=manager
        )

        self.trainButton = UIButton(
            relative_rect=pygame.FRect((self.width * .125, self.height * .5), (self.width * .75, self.height * .3)),
            text="Train Perceptron",
            manager=manager,
            container=self.uiPanel,
        )

        self.groupOneButton = UIButton(
            relative_rect=pygame.FRect((self.width * .08, self.height * .1), (self.width  * .38, self.height * .3)),
            text="Group 1",
            manager=manager,
            container=self.uiPanel,
            toggle_button=True
        )

        self.groupTwoButton = UIButton(
            relative_rect=pygame.FRect((self.width * .51, self.height * .1), (self.width  * .38, self.height * .3)),
            text="Group 2",
            manager=manager,
            container=self.uiPanel,
            toggle_button=True
        )

        # Group buttons
        self.buttonGroup =ToggleButtonGroup([self.groupOneButton, self.groupTwoButton])
    
    @property
    def mouseInPanel(self) -> bool:
        mousePos = pygame.mouse.get_pos()
        panelRect = self.uiPanel.get_abs_rect()

        return panelRect.collidepoint(mousePos)
    
    def process_event(self, event: pygame.Event) -> None:
        self.buttonGroup.process_event(event)