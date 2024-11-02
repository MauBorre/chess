import font

class Font_1: ...

class ScreenDrawer:
    def __init__(self, screen):
        self.screen = screen

    def draw_text(self,text,color,x,y,center=True,font_size='large'):
        _font = font.large_font if font_size=='large' else font.medium_font
        surface = self.master.screen
        textobj = _font.render(text,1,color)
        text_width = textobj.get_width()
        text_height = textobj.get_height()
        textrect = textobj.get_rect()
        if center: textrect.topleft = (x - text_width/2, y - text_height/2) # anchors placement at center
        else: textrect.topleft = (x,y)
        surface.blit(textobj,textrect)

class MainMenuDrawer(ScreenDrawer): ...

class MatchDrawer(ScreenDrawer):
    def __init__(self, screen):
        super().__init__(screen)

    def draw_match_mode(self):
        self.draw_text(self._instructions['mode'], Font_1, size=20)

    def draw_HUD_title(self):
        ...
