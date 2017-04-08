from datetime import datetime

from kivy.app import App
from kivy.core.window import Window
from kivy.graphics.texture import Texture
from kivy.properties import ListProperty

from probonobo.action import DragAction, SelectAction
from probonobo.device.android import AndroidDevice
from probonobo.session import Session


class ProbonoboToolApp(App):
    marquee_rect = ListProperty((0,) * 4)

    session = None

    prepared_action = None

    def build(self):
        super().build()

        Window.bind(mouse_pos=self.update_display)

        self.session = Session(device=AndroidDevice())
        self.session.begin()

        self.update_image()

    def update_image(self):
        start = datetime.now()
        image_bytes, width, height, format = self.session.device.get_screenshot_bytes()
        print(datetime.now() - start)
        texture = Texture.create(size=(width, height))
        texture.blit_buffer(image_bytes, colorfmt='rgba', bufferfmt='ubyte')
        texture.flip_vertical()
        self.root.ids.image.texture = texture

    def update_display(self, window, pos):
        display = self.root.ids.display

        device_pos = self._window_pos_to_device_pos(pos)

        if device_pos is None:
            display.text = ''
        else:
            display.text = str(device_pos)

    def update_action(self):
        if isinstance(self.prepared_action, SelectAction):
            self.root.ids.last_action.text = 'Select at ' + str(self.prepared_action.coords)
        elif isinstance(self.prepared_action, DragAction):
            self.root.ids.last_action.text = \
                'Drag from ' + str(self.prepared_action.start) + \
                ' to ' + str(self.prepared_action.end) + \
                ' over ' + ('%.02f' % self.prepared_action.duration) + 's'
        else:
            self.root.ids.last_action.text = ''

    def execute_action(self):
        self.session.perform_actions([self.prepared_action])

    def capture_region(self):
        texture = self.root.ids.image.texture
        region_width, region_height = (e - s for s, e in zip(self.prepared_action.start, self.prepared_action.end))
        region = (self.prepared_action.start[0],
                  texture.height - self.prepared_action.start[1] - region_height,
                  region_width,
                  region_height)
        region_texture = self.root.ids.image.texture.get_region(*region)
        region_texture.save('captured.png')

    def handle_select_start(self, widget, touch):
        if touch.button == 'left':
            self.marquee_rect = (0,) * 4

    def handle_drag(self, widget, touch):
        if touch.button == 'left':
            start_device_pos = self._window_pos_to_device_pos(touch.opos)
            end_device_pos = self._window_pos_to_device_pos(touch.pos)
            if start_device_pos is not None and end_device_pos is not None:
                min_coord = tuple(min(s, e) for s, e in zip(touch.opos, touch.pos))
                max_coord = tuple(max(s, e) for s, e in zip(touch.opos, touch.pos))
                self.marquee_rect = (min_coord[0], min_coord[1],
                                     max_coord[0] - min_coord[0], max_coord[1] - min_coord[1])


    def handle_select(self, widget, touch):
        if touch.button == 'left':
            start_device_pos = self._window_pos_to_device_pos(touch.opos)
            end_device_pos = self._window_pos_to_device_pos(touch.pos)
            if start_device_pos is not None and end_device_pos is not None:
                delta = tuple(e - s for s, e in zip(start_device_pos, end_device_pos))
                mag_squared = sum(n ** 2 for n in delta)
                if mag_squared < 2:
                    self.prepared_action = SelectAction(coords=end_device_pos)
                    self.update_action()
                    #self.root.ids.last_action.text = 'Select at ' + str(end_device_pos)
                    #self.device.select_at_coord(end_device_pos)
                else:
                    #self.root.ids.last_action.text = 'From ' + str(start_device_pos) + ' to ' + str(end_device_pos)

                    min_coord = tuple(min(s, e) for s, e in zip(touch.opos, touch.pos))
                    max_coord = tuple(max(s, e) for s, e in zip(touch.opos, touch.pos))
                    self.marquee_rect = (min_coord[0], min_coord[1],
                                         max_coord[0] - min_coord[0], max_coord[1] - min_coord[1])

                    self.prepared_action = DragAction(start=start_device_pos, end=end_device_pos,
                                                      duration=(touch.time_end - touch.time_start))
                    self.update_action()


    def _window_pos_to_device_pos(self, window_pos):
        image = self.root.ids.image
        local_pos = tuple((wp - fo - (fs - ns) / 2) * ts / ns
                          for wp, fo, fs, ns, ts
                          in zip(window_pos, image.pos, image.size, image.norm_image_size, image.texture_size))
        in_bounds = tuple(p >= 0 and p < s for p, s in zip(local_pos, image.texture_size))

        if all(in_bounds):
            return (round(local_pos[0]), round(image.texture_size[1] - local_pos[1]))
        else:
            return None

if __name__ == '__main__':
    ProbonoboToolApp().run()