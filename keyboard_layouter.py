import pcbnew
import wx
import json
import math
import sys
import traceback

SWITCH_REF_PREFIX = 'SW'
DIODE_REF_PREFIX = 'D'
KEY_UNIT_SIZE_MM = 19.05

KEY_OFFSET = {
    '1':  0,  # 12.065
    '1.25':  2.381,  # 14.446
    '1.5':  4.763,  # 16.828
    '1.75':  7.144,  # 19.209
    '2':  9.525,  # 21.590
    '2.25': 11.9806,  # 23.971
    '2.75': 16.669,  # 28.734
    '6.25': 50.006,  # 62.071
}

KEY_ORIGIN = {
    ('1', '1'): (12.065, 4.445),
    ('1', '2'): (12.065, 13.97),
    ('1.25', '1'): (14.446, 4.445),
    ('1.5', '1'): (16.828, 4.445),
    ('1.75', '1'): (19.209, 4.445),
    ('2', '1'): (21.590, 4.445),
    ('2.25', '1'): (23.971, 4.445),
    ('2.75', '1'): (28.734, 4.445),
    ('6.25', '1'): (62.071, 4.445),
}

DEFAULT_PARAMS = {
    'json': {
        'file': '',
        'data': [],
    },
    'switch': {
        'move': True,
    },
    'diode': {
        'move': False,
        'offset_x_mm': '0',  # -8.6725
        'offset_y_mm': '0',  # 8.59
        'flip': False,
    },
}


class KeyboardLayouter(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = 'Keyboard Layouter'
        self.category = 'Modify PCB'
        self.description = 'Move parts to the position specified by json'
        self.__version__ = '0.1.1'

    def Run(self):
        self.__gui()

    @property
    def version(self):
        return self.__version__

    def __run(self, params):
        self.params = params
        self.status = 'ok'
        self.messages = []

        self.board = pcbnew.GetBoard()
        self.__execute()
        pcbnew.Refresh()

        return self.status, self.messages

    def __execute(self):
        props = {
            'x': 0,
            'y': 0,
            'w': 1,
            'h': 1,
            'r': 0,
            'rx': 0,
            'ry': 0,
        }
        reset_x = reset_y = 0
        for y, row in enumerate(self.params['json']['data']):
            for element in row:
                if type(element) is dict:
                    r = element.get('r')
                    rx = element.get('rx')
                    ry = element.get('ry')

                    if r is not None:
                        props['r'] = r
                    if rx is not None:
                        props['rx'] = reset_x = rx
                    if ry is not None:
                        props['ry'] = reset_y = ry
                    if (rx is not None) or (ry is not None):
                        props['x'] = reset_x
                        props['y'] = reset_y

                    props['x'] += element.get('x', 0)
                    props['y'] += element.get('y', 0)
                    props['w'] = element.get('w', 1)
                    props['h'] = element.get('h', 1)
                else:
                    ref_id = element.split("\n")[0].strip()  # top left legend is used as ref_id
                    self.__check_key_size(ref_id, props)
                    self.__move_parts(ref_id, props)
                    props['x'] += props['w']
                    props['w'] = 1
                    props['h'] = 1
            props['x'] = reset_x
            props['y'] += 1

    def __check_key_size(self, ref_id, props):
        w, h = str(props['w']), str(props['h'])
        r = -props['r']
        flag = False

        if (KEY_OFFSET.get(w) is None) or (KEY_OFFSET.get(h) is None):
            flag = True

        if (r != 0) and (KEY_ORIGIN.get((w, h)) is None):
            flag = True

        if flag:
            self.status = 'warning'
            self.messages.append(
                '%s is ( w, h )=( %s, %s ). This size is not applicable.' % (self.__sw_ref(ref_id), w, h)
            )

    @staticmethod
    def __sw_ref(ref_id):
        return '%s%s' % (SWITCH_REF_PREFIX, ref_id)

    @staticmethod
    def __diode_ref(ref_id):
        return '%s%s' % (DIODE_REF_PREFIX, ref_id)

    @staticmethod
    def __rotate(deg, x, y, x0=0, y0=0):
        rad = math.pi * deg / 180.0
        xd = math.cos(rad) * (x - x0) + math.sin(rad) * (y - y0)
        yd = -math.sin(rad) * (x - x0) + math.cos(rad) * (y - y0)
        return xd + x0, yd + y0

    def __move_parts(self, ref_id, props):
        x, y, w, h = props['x'], props['y'], str(props['w']), str(props['h'])
        r, rx, ry = -props['r'], props['rx'], props['ry']

        x_mm = KEY_UNIT_SIZE_MM * x + KEY_OFFSET.get(w, 0)
        y_mm = KEY_UNIT_SIZE_MM * y + KEY_OFFSET.get(h, 0)

        rx_mm = KEY_UNIT_SIZE_MM * rx - KEY_ORIGIN.get((w, h), (0, 0))[0] + KEY_OFFSET.get(w, 0)
        ry_mm = KEY_UNIT_SIZE_MM * ry - KEY_ORIGIN.get((w, h), (0, 0))[1] + KEY_OFFSET.get(h, 0)
        x_mm, y_mm = self.__rotate(r, x_mm, y_mm, rx_mm, ry_mm)

        if self.params['switch']['move']:
            sw = self.board.FindModule(self.__sw_ref(ref_id))
            if sw is not None:
                sw.SetPosition(pcbnew.wxPointMM(x_mm, y_mm))
                sw.SetOrientationDegrees(r)

        if self.params['diode']['move']:
            diode = self.board.FindModule(self.__diode_ref(ref_id))
            if diode is not None:
                diode.SetPosition(pcbnew.wxPointMM(x_mm, y_mm))
                dx_mm, dy_mm = self.__rotate(r,
                                             self.params['diode']['offset_x_mm'],
                                             self.params['diode']['offset_y_mm'])
                diode.Move(pcbnew.wxPointMM(dx_mm, dy_mm))

                if self.params['diode']['move']:
                    diode.Flip(diode.GetCenter())
                diode.SetOrientationDegrees(r)

    def __gui(self):
        WINDOW_SIZE = (600, 350)
        MARGIN_PIX = 10
        INDENT_PIX = 20

        params = DEFAULT_PARAMS.copy()

        def frame_title():
            return '%s (%s)' % (self.name, self.version)

        def set_initial_checkbox(checkbox, enable, value):
            if enable:
                checkbox.Enable()
            else:
                checkbox.Disable()
            checkbox.SetValue(value)

        def set_initial_textctrl(textctrl, enable, value):
            if enable:
                textctrl.Enable()
            else:
                textctrl.Disable()
            textctrl.SetValue(str(value))

        class FilePanel(wx.Panel):
            def __init__(self, parent):
                def textctrl_handler(_):
                    params['json']['file'] = textctrl.GetValue()

                def button_handler(_):
                    dialog = wx.FileDialog(None, 'Select a file', '', '',
                                           'JSON file(*.json)|*.json|All files|*.*',
                                           wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
                    if dialog.ShowModal() == wx.ID_OK:
                        textctrl.SetValue(dialog.GetPath())
                    else:
                        textctrl.SetValue('')

                super(FilePanel, self).__init__(parent, wx.ID_ANY)

                text = wx.StaticText(self, wx.ID_ANY, 'JSON file:')

                textctrl = wx.TextCtrl(self, wx.ID_ANY)
                set_initial_textctrl(textctrl, True, params['json']['file'])
                textctrl.Bind(wx.EVT_TEXT, textctrl_handler)

                button = wx.Button(self, wx.ID_ANY, 'Select')
                button.Bind(wx.EVT_BUTTON, button_handler)

                layout = wx.BoxSizer(wx.HORIZONTAL)
                layout.Add(text, flag=wx.ALIGN_CENTER)
                layout.Add(textctrl, proportion=1, flag=wx.ALIGN_CENTER | wx.LEFT, border=MARGIN_PIX)
                layout.Add(button, flag=wx.ALIGN_CENTER | wx.LEFT, border=MARGIN_PIX)
                self.SetSizer(layout)

        class SwitchPanel(wx.Panel):
            def __init__(self, parent):
                def checkbox_move_handler(_):
                    params['switch']['move'] = checkbox_move.GetValue()

                super(SwitchPanel, self).__init__(parent, wx.ID_ANY)

                checkbox_move = wx.CheckBox(self, wx.ID_ANY, 'Switch')
                set_initial_checkbox(checkbox_move, True, params['switch']['move'])
                checkbox_move.Bind(wx.EVT_CHECKBOX, checkbox_move_handler)

                layout = wx.BoxSizer(wx.HORIZONTAL)
                layout.Add(checkbox_move)
                self.SetSizer(layout)

        class DiodePanel(wx.Panel):
            def __init__(self, parent):
                def checkbox_move_handler(_):
                    params['diode']['move'] = checkbox_move.GetValue()
                    if params['diode']['move']:
                        textctrl_offset_x_mm.Enable()
                        textctrl_offset_y_mm.Enable()
                        checkbox_flip.Enable()
                    else:
                        textctrl_offset_x_mm.Disable()
                        textctrl_offset_y_mm.Disable()
                        checkbox_flip.Disable()

                def textctrl_offset_x_mm_handler(_):
                    params['diode']['offset_x_mm'] = textctrl_offset_x_mm.GetValue()

                def textctrl_offset_y_mm_handler(_):
                    params['diode']['offset_y_mm'] = textctrl_offset_y_mm.GetValue()

                def checkbox_flip_handler(_):
                    params['diode']['flip'] = checkbox_flip.GetValue()

                super(DiodePanel, self).__init__(parent, wx.ID_ANY)

                checkbox_move = wx.CheckBox(self, wx.ID_ANY, 'Diode')
                set_initial_checkbox(checkbox_move, True, params['diode']['move'])
                checkbox_move.Bind(wx.EVT_CHECKBOX, checkbox_move_handler)

                panel_offset_x_mm = wx.Panel(self, wx.ID_ANY)
                text_offset_x_mm = wx.StaticText(panel_offset_x_mm, wx.ID_ANY, 'Offset x[mm]:')
                textctrl_offset_x_mm = wx.TextCtrl(panel_offset_x_mm, wx.ID_ANY)
                set_initial_textctrl(textctrl_offset_x_mm,
                                     params['diode']['move'],
                                     params['diode']['offset_x_mm'])
                textctrl_offset_x_mm.Bind(wx.EVT_TEXT, textctrl_offset_x_mm_handler)
                layout_offset_x_mm = wx.BoxSizer(wx.HORIZONTAL)
                layout_offset_x_mm.Add(text_offset_x_mm, flag=wx.ALIGN_CENTER)
                layout_offset_x_mm.Add(textctrl_offset_x_mm, flag=wx.ALIGN_CENTER | wx.LEFT, border=MARGIN_PIX)
                panel_offset_x_mm.SetSizer(layout_offset_x_mm)

                panel_offset_y_mm = wx.Panel(self, wx.ID_ANY)
                text_offset_y_mm = wx.StaticText(panel_offset_y_mm, wx.ID_ANY, 'Offset y[mm]:')
                textctrl_offset_y_mm = wx.TextCtrl(panel_offset_y_mm, wx.ID_ANY)
                set_initial_textctrl(textctrl_offset_y_mm,
                                     params['diode']['move'],
                                     params['diode']['offset_y_mm'])
                textctrl_offset_y_mm.Bind(wx.EVT_TEXT, textctrl_offset_y_mm_handler)
                layout_offset_y_mm = wx.BoxSizer(wx.HORIZONTAL)
                layout_offset_y_mm.Add(text_offset_y_mm, flag=wx.ALIGN_CENTER)
                layout_offset_y_mm.Add(textctrl_offset_y_mm, flag=wx.ALIGN_CENTER | wx.LEFT, border=MARGIN_PIX)
                panel_offset_y_mm.SetSizer(layout_offset_y_mm)

                checkbox_flip = wx.CheckBox(self, wx.ID_ANY, 'Flip')
                set_initial_checkbox(checkbox_flip, False, params['diode']['move'])
                checkbox_flip.Bind(wx.EVT_CHECKBOX, checkbox_flip_handler)

                layout = wx.BoxSizer(wx.VERTICAL)
                layout.Add(checkbox_move)
                layout.Add(panel_offset_x_mm, flag=wx.LEFT, border=INDENT_PIX)
                layout.Add(panel_offset_y_mm, flag=wx.LEFT, border=INDENT_PIX)
                layout.Add(checkbox_flip, flag=wx.LEFT, border=INDENT_PIX)
                self.SetSizer(layout)

        class RunPanel(wx.Panel):
            def __init__(self, parent, callback, top_frame):
                def button_run_handler(_):
                    try:
                        p = self.__pre_process(params)
                        status, messages = callback(p)
                        if status == 'warning':
                            wx.MessageBox('\n'.join(messages), 'Warning', style=wx.OK | wx.ICON_WARNING)
                        top_frame.Close(True)
                    except IOError:
                        wx.MessageBox('Keyboard Layouter cannot open this file.\n\n%s' % params['json']['file'],
                                      'Error: File cannot be opened', style=wx.OK | wx.ICON_ERROR)
                    except ValueError:
                        wx.MessageBox('Keyboard Layouter cannot parse this json file.\n\n%s' % params['json']['file'],
                                      'Error: File cannot be parsed', style=wx.OK | wx.ICON_ERROR)
                    except Exception:
                        t, v, tb = sys.exc_info()
                        wx.MessageBox('\n'.join(traceback.format_exception(t, v, tb)),
                                      'Execution failed', style=wx.OK | wx.ICON_ERROR)
                    finally:
                        return

                super(RunPanel, self).__init__(parent, wx.ID_ANY)
                button = wx.Button(self, wx.ID_ANY, 'Run')
                button.Bind(wx.EVT_BUTTON, button_run_handler)

                layout = wx.BoxSizer(wx.VERTICAL)
                layout.Add(button, 0, wx.GROW)
                self.SetSizer(layout)

            def __pre_process(self, p):
                p['json']['data'] = self.__load_json(p)
                p['diode']['offset_x_mm'] = float(p['diode']['offset_x_mm'])
                p['diode']['offset_y_mm'] = float(p['diode']['offset_y_mm'])
                return p

            @staticmethod
            def __load_json(p):
                with open(p['json']['file'], 'r') as f:
                    json_data = json.load(f)

                    # remove keyboard metadata
                    if type(json_data[0]) is dict:
                        json_data = json_data[1:]
                return json_data

        class TopFrame(wx.Frame):
            def __init__(self, title, callback):
                super(TopFrame, self).__init__(None, wx.ID_ANY, title, size=WINDOW_SIZE)

                root_panel = wx.Panel(self, wx.ID_ANY)

                file_panel = FilePanel(root_panel)
                switch_panel = SwitchPanel(root_panel)
                diode_panel = DiodePanel(root_panel)
                run_panel = RunPanel(root_panel, callback, self)

                root_layout = wx.BoxSizer(wx.VERTICAL)
                root_layout.Add(file_panel, 0, wx.GROW | wx.ALL, border=MARGIN_PIX)
                root_layout.Add(switch_panel, 0, wx.GROW | wx.ALL, border=MARGIN_PIX)
                root_layout.Add(diode_panel, 0, wx.GROW | wx.ALL, border=MARGIN_PIX)
                root_layout.Add(run_panel, 0, wx.GROW | wx.ALL, border=MARGIN_PIX)

                root_panel.SetSizer(root_layout)
                root_layout.Fit(root_panel)

        frame = TopFrame(frame_title(), self.__run)
        frame.Center()
        frame.Show()


KeyboardLayouter().register()

