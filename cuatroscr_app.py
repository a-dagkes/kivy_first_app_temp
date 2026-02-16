from kivy.app import App
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

from random import random


SPACE = 5
FONT_SIZE = '20sp'
MIN_HEIGHT = 35
MIN_WIDTH = 150


class ScrollLabel(ScrollView):
    '''Сложносоченённый ScrollView плюс Label'''

    def __init__(self, text, **kwargs):
        super().__init__(**kwargs)
        self.label = Label(
            text=text, markup=True,
            size_hint_y=None,
            font_size=FONT_SIZE,
            halign='left', valign='top',
        )
        self.label.bind(size=self.resize)
        self.add_widget(self.label)

    def resize(self, *argv):
        self.label.text_size = (self.label.width, None)
        self.label.texture_update()
        self.label.height = self.label.texture_size[1]

    def on_touch_down(self, touch):
        if touch.button == 'left' and self.collide_point(*touch.pos):
            if touch.x > self.right - 2 * self.bar_width:
                relative_y = (touch.y - self.y) / self.height
                self.scroll_y = relative_y
                touch.grab(self)
                return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            relative_y = (touch.y - self.y) / self.height
            self.scroll_y = max(0, min(1, relative_y))
            return True
        return super().on_touch_move(touch)


class ScrButton(Button):
    '''Кнопка для переключения между экранами'''

    def __init__(self, screen, direction='right', goal='main', **kwargs):
        super().__init__(**kwargs)
        self.screen = screen
        self.direction = direction
        self.goal = goal

    def on_press(self):
        self.screen.manager.transition.direction = self.direction
        self.screen.manager.current = self.goal


class MainScr(Screen):
    '''Основной экран-меню'''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        label = Label(text='Выбери экран', font_size=FONT_SIZE)
        btn_to_first = ScrButton(self, direction='down', goal='first', text='1')
        btn_to_second = ScrButton(self, direction='left', goal='second', text='2')
        btn_to_third = ScrButton(self, direction='up', goal='third', text='3')
        btn_to_fourth = ScrButton(self, direction='right', goal='fourth', text='4')

        left_layout = BoxLayout(orientation='vertical')
        left_layout.add_widget(label)
        right_layout = BoxLayout(
            orientation='vertical',
            spacing=SPACE,
        )
        right_layout.add_widget(btn_to_first)
        right_layout.add_widget(btn_to_second)
        right_layout.add_widget(btn_to_third)
        right_layout.add_widget(btn_to_fourth)
        mainlayout = BoxLayout(padding=2 * SPACE, spacing=SPACE)
        mainlayout.add_widget(left_layout)
        mainlayout.add_widget(right_layout)
        self.add_widget(mainlayout)


class FirstScr(Screen):
    '''Экран из кнопок, расположенных по диагонали'''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        btn_blank = Button(
            text='Выбор: 1',
            size_hint=(.5, .5),
            pos_hint={'right': .5},
            on_press=self.change_color,
        )
        btn_to_main = ScrButton(
            self, direction='up', text='Назад',
            size_hint=(.5, .5),
            pos_hint={'right': 1},
        )
        main_layout = BoxLayout(
            orientation='vertical',
            size_hint=(.5, .5),
            pos_hint={'center_x': .5, 'center_y': .5},
        )
        main_layout.add_widget(btn_blank)
        main_layout.add_widget(btn_to_main)
        self.add_widget(main_layout)

    def change_color(self, widget):
        widget.color = (random(), random(), random(), 1)


class SecondScr(Screen):
    '''Экран с TextInput для ввода пароля'''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.label = Label(
            text='Выбор: 2',
            font_size=FONT_SIZE,
            size_hint=(1, .8),
        )

        self.psswrd_comment = Label(
            text='Введите пароль:',
            font_size=FONT_SIZE,
            size_hint=(None, 1), width=MIN_WIDTH,
        )
        self.psswrd_input = TextInput(
            hint_text='Ваш пароль',
            multiline=False,
            font_size=FONT_SIZE,
            size_hint=(None, 1), width=2 * MIN_WIDTH,
            pos_hint={'right': 0},
        )
        psswrd_line = BoxLayout(
            size_hint=(None, None),
            height=MIN_HEIGHT,
            pos_hint={'center_x': .5, 'center_y': .5},
            spacing=SPACE,
        )
        psswrd_line.add_widget(self.psswrd_comment)
        psswrd_line.add_widget(self.psswrd_input)
        psswrd_line.bind(minimum_width=psswrd_line.setter('width'))
        Window.bind(size=self.on_resize)

        btn_ok = Button(text='Ok!', on_release=self.change_label)
        btn_to_main = ScrButton(self, direction='right', text='Назад')
        btn_line = BoxLayout(
            size_hint=(.75, .2),
            pos_hint={'center_x': .5, 'center_y': .5},
            spacing=SPACE,
        )
        btn_line.add_widget(btn_ok)
        btn_line.add_widget(btn_to_main)

        main_layout = BoxLayout(
            orientation='vertical',
            padding=2 * SPACE, spacing=SPACE,
        )
        main_layout.add_widget(self.label)
        main_layout.add_widget(psswrd_line)
        main_layout.add_widget(btn_line)
        self.add_widget(main_layout)

    def on_resize(self, widget, value):
        width, _ = value
        self.psswrd_input.width = min(2 * MIN_WIDTH, width - 2 * SPACE)
        if width < 3 * MIN_WIDTH:
            self.psswrd_comment.width = 0
            self.psswrd_comment.opacity = 0
        elif not self.psswrd_comment.opacity:
            self.psswrd_comment.opacity = 1
            self.psswrd_comment.width = MIN_WIDTH

    def change_label(self, widget):
        if self.psswrd_input.text.strip():
            self.label.text = '*' * len(self.psswrd_input.text.strip())
            self.psswrd_input.text = ''

    def on_leave(self, *args):
        self.psswrd_input.text = ''


class ThirdScr(Screen):
    '''Экран с таймером и прогресс-баром'''
    DURATION = 60
    cur_sec = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.timer = None
        label = Label(
            text='Минутный таймер',
            font_size=FONT_SIZE,
            size_hint=(1, .1),
        )
        self.progress = ProgressBar(
            max=self.DURATION, value=0,
            size_hint=(1, None), height=int(MIN_HEIGHT * 0.5),
        )
        self.bind(cur_sec=self.update_progress)
        self.btn_control = Button(
            text='3',
            size_hint=(.75, .75),
            pos_hint={'center_x': .5, 'center_y': .5},
            on_release=self.on_click,
        )
        self.btn_control.original_color = self.btn_control.color
        btn_to_main = ScrButton(
            self, direction='down', text='Назад',
            size_hint=(1, .1),
            pos_hint={'center_y': .5},
        )
        main_layout = BoxLayout(
            orientation='vertical',
            padding=2 * SPACE, spacing=SPACE,
        )
        main_layout.add_widget(label)
        main_layout.add_widget(self.progress)
        main_layout.add_widget(self.btn_control)
        main_layout.add_widget(btn_to_main)
        self.add_widget(main_layout)

    def on_pre_enter(self, *args):
        self.btn_control.text = '3'
        self.btn_control.color = self.btn_control.original_color
        self.cur_sec = 0

    def on_leave(self, *args):
        if self.timer:
            self.timer.cancel()
            self.timer = None

    def on_click(self, widget):
        if widget.text == '3':
            widget.text = '2'
        elif widget.text == '2':
            widget.text = '1'
        elif widget.text == '1':
            widget.text = 'Минута пошла'
            self.timer = Clock.schedule_interval(self.update_timer, 1)
        elif widget.text == 'Минута прошла':
            try:
                widget.color = widget.original_color
            except AttributeError:
                widget.color = (1, 1, 1, 1)
            widget.text = '3'
            self.cur_sec = 0

    def update_progress(self, instance, value):
        self.progress.value = value

    def update_timer(self, dt):
        self.cur_sec += dt  # + прошедшее число секунд с прошлого обновления
        if self.cur_sec >= self.DURATION:
            self.timer.cancel()
            self.btn_control.color = (0.9, 0.1, 0.1, 1)
            self.btn_control.text = 'Минута прошла'
            self.timer = None


class FourthScr(Screen):
    '''Экран с длиииииинным текстом и полосой прокрутки'''
    DEFAULT_TEXT = 'How much wood would a woodchuck chuck if a woodchuck could chuck wood?\n'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        btn_to_main = ScrButton(
            self, direction='left', text='Назад',
            size_hint=(1, .1),
        )
        self.gran_label = ScrollLabel(
            text=self.DEFAULT_TEXT * 200,
            bar_width=2 * SPACE,
        )
        main_layout = BoxLayout(
            orientation='vertical',
            padding=2 * SPACE, spacing=SPACE,
        )
        main_layout.add_widget(self.gran_label)
        main_layout.add_widget(btn_to_main)
        self.add_widget(main_layout)

    def on_enter(self):
        self.gran_label.scroll_y = 1


class CuatroScrApp(App):
    '''Приложение с одним экраном-меню и четырьмя экранами с функционалом'''

    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScr(name='main'))
        sm.add_widget(FirstScr(name='first'))
        sm.add_widget(SecondScr(name='second'))
        sm.add_widget(ThirdScr(name='third'))
        sm.add_widget(FourthScr(name='fourth'))
        return sm


app = CuatroScrApp()
app.run()
