class Font_1: ...

class ScreenDrawer:
    def __init__(self, screen):
        self.screen = screen

    def draw_text(): ...

class MainMenuDrawer(ScreenDrawer): ...

class MatchDrawer(ScreenDrawer):
    def __init__(self, screen):
        super().__init__(screen)

    def draw_match_mode(self):
        self.draw_text(self._instructions['mode'], Font_1, size=20)

    def draw_HUD_title(self):
        ...
