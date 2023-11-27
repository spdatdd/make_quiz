from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.recycleview import MDRecycleView
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.list import OneLineIconListItem
from kivymd.uix.textfield import MDTextField
from kivy.properties import ObjectProperty, StringProperty, NumericProperty, BooleanProperty, ListProperty
from kivy.clock import Clock
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior

class LoginScreen(MDScreen):
    pass

class RegisterScreen(MDScreen):
    pass

class ContentNavigationDrawer(MDScrollView):
    screen_manager = ObjectProperty()
    nav_drawer = ObjectProperty()

class NavigationDrawerMenu(MDScreen):
    pass

class IconListItem(OneLineIconListItem):
    icon = StringProperty()

class Choice(MDBoxLayout):
    pass

class YourThink(MDBoxLayout):
    pass

class Question(MDBoxLayout):
    pass

class ImageMedia(MDBoxLayout):
    pass

class AudioMedia(MDBoxLayout):
    path_txt = StringProperty('')
    audio = ObjectProperty({})
    position_progress = NumericProperty(0)

class VideoMedia(MDBoxLayout):
    pass

class CreateExamScreen(MDScreen):
    mode = StringProperty('')

class CaNhan(MDGridLayout):
    pass

class BottomNavigation(MDScreen):
    pass

class DoExam(MDScreen):
    name_exam = StringProperty('')

class TrangThi(MDBoxLayout):
    dap_an_chinh_xac = ListProperty([])
    id_cau_hoi = NumericProperty()

class DapAnExam(MDBoxLayout):
    pass

class DapAnDienExam(MDBoxLayout):
    pass

class AudioExam(MDBoxLayout):
    path_txt = StringProperty('')
    audio = ObjectProperty({})
    position_progress = NumericProperty(0)

class List_Exam(MDBoxLayout):
    pass

class UserCard(RecycleDataViewBehavior, MDBoxLayout):
    text = StringProperty()
    id = NumericProperty()
    callback = ObjectProperty(lambda x: x)
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)
    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        return super().refresh_view_attrs(rv, index, data)
    def on_touch_down(self, touch):
        if super().on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            if self.selected:
                Clock.schedule_once(self.callback)
            return self.parent.select_with_touch(self.index, touch)
    def apply_selection(self, rv, index, is_selected):
        self.selected = is_selected
        rv.data[index]["selected"] = is_selected

class HomeCard(RecycleDataViewBehavior, MDBoxLayout):
    text = StringProperty()
    id = NumericProperty()
    chu_de = StringProperty()
    callback = ObjectProperty(lambda x: x)
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)
    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        return super().refresh_view_attrs(rv, index, data)
    def on_touch_down(self, touch):
        if super().on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            if self.selected:
                Clock.schedule_once(lambda x:self.callback(self.text, self.id), 0.1)
            return self.parent.select_with_touch(self.index, touch)
    def apply_selection(self, rv, index, is_selected):
        self.selected = is_selected
        rv.data[index]["selected"] = is_selected

class SelectableRecycleGridLayout(FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout):
    pass

class Custom_content(MDTextField):
    pass

class ManHinhKetQua(MDScreen):
    ten_bai_thi = StringProperty('')

class ManHinhChiTietKetQua(MDScreen):
    ten_bai_thi = StringProperty('')

class ManHinhHome(MDRelativeLayout):
    pass

class FixedRecycleView(MDRecycleView):
    distance_to_top = NumericProperty()
    scrollable_distance = NumericProperty()
    def on_scrollable_distance(self, *args):
        if self.scroll_y > 0 and self.scrollable_distance > 0:
            self.scroll_y = (self.scrollable_distance - self.distance_to_top) / self.scrollable_distance
