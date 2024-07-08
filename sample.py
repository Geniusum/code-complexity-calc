from os_touch.init import *
from os_touch.utils import *
import os_touch.flux as flux

FLUX = flux.Flux()


class MITouch():
    def __init__(self):
        self.parameters = {
            "cam_port": 0,
            "resized": False,
            "manual_border": False,
            "default_fps": 74,
            "display_monitor": -1,
            "control_monitor": 0,
            "click_sensibility": 8,
            "ds_points_size": 40,
            "pvw_points_size": 10,
            "cam_flip_v": False,
            "cam_flip_h": False
        }

        self.cam = cv2.VideoCapture(self.getParameter("cam_port"))
        self.image_on_canvas = None

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands()

        self.fps = self.getParameter("default_fps")

        self.monitors_areas_ = monitor_areas()
        self.monitor_areas = self.monitors_areas_[
            self.getParameter("display_monitor")]

        self.controller = tk.Tk()

        self.preview_canvas = tk.Canvas(
            self.controller, highlightthickness=0, background="#121212")
        self.preview_canvas.pack(fill="both", expand=True)

        self.result, self.wc_image = self.cam.read()
        self.wc_height, self. wc_width, self.wc_channels = self.wc_image.shape

        self.cn_width = self.wc_width
        self.cn_height = self.wc_height

        self.sc_w = self.monitors_areas_[
            self.getParameter("control_monitor")][4]
        self.sc_h = self.monitors_areas_[
            self.getParameter("control_monitor")][5]

        self.controller.geometry(
            f"{self.cn_width}x{self.cn_height}+{int(self.sc_w / 2 - self.cn_width / 2)}+{int(self.sc_h / 2 - self.cn_height / 2)}")

        self.display = tk.Toplevel(self.controller)
        self.display.config(background="black")

        self.display.overrideredirect(True)

        self.display.geometry(
            f"{self.monitor_areas[4]}x{self.monitor_areas[5]}+{self.monitor_areas[0]}+{self.monitor_areas[1]}")

        self.pvw_points = []
        self.pvw_pointA_x = int(self.cn_width * 2/10)
        self.pvw_pointA_y = int(self.cn_height * 2/10)
        self.pvw_pointB_x = int(self.cn_width * 8/10)
        self.pvw_pointB_y = int(self.cn_height * 8/10)

        self.landmarks_canvas = []

        self.cursor_states = {}

        self.act_f = 0
        self.act_fps = 0
        self.act_fps_time = time.time()

        self.menu = [
            {
                "name": "Preview",
                "type": "menu",
                "items": [
                    {
                        "name": "Change FPS",
                        "type": "menu",
                        "items": [
                            {
                                "name": "Decrease 50",
                                "type": "option",
                                "function": lambda: self.change_fps(-50)
                            },
                            {
                                "name": "Decrease 20",
                                "type": "option",
                                "function": lambda: self.change_fps(-20)
                            },
                            {
                                "name": "Decrease 10",
                                "type": "option",
                                "function": lambda: self.change_fps(-10)
                            },
                            {
                                "name": "Decrease 5",
                                "type": "option",
                                "function": lambda: self.change_fps(-5)
                            },
                            {
                                "name": "Decrease 2",
                                "type": "option",
                                "function": lambda: self.change_fps(-2)
                            },
                            {
                                "name": "Decrease 1",
                                "type": "option",
                                "function": lambda: self.change_fps(-1)
                            },
                            {
                                "name": f"Reset to {self.getParameter('default_fps')}",
                                "type": "option",
                                "function": lambda: self.change_fps(self.getParameter('default_fps'), True)
                            },
                            {
                                "name": "Increase 1",
                                "type": "option",
                                "function": lambda: self.change_fps(1)
                            },
                            {
                                "name": "Increase 2",
                                "type": "option",
                                "function": lambda: self.change_fps(2)
                            },
                            {
                                "name": "Increase 5",
                                "type": "option",
                                "function": lambda: self.change_fps(5)
                            },
                            {
                                "name": "Increase 10",
                                "type": "option",
                                "function": lambda: self.change_fps(10)
                            },
                            {
                                "name": "Increase 20",
                                "type": "option",
                                "function": lambda: self.change_fps(20)
                            },
                            {
                                "name": "Increase 50",
                                "type": "option",
                                "function": lambda: self.change_fps(50)
                            }
                        ]
                    },
                    {
                        "name": "Webcam resize",
                        "type": "option",
                        "function": self.change_resized
                    }
                ]
            },
            {
                "name": "Display",
                "type": "menu",
                "items": [
                    {
                        "name": "Borders",
                        "type": "menu",
                        "items": [
                            {
                                "name": "Manual/Auto",
                                "type": "option",
                                "function": self.change_border_mode
                            }
                        ]
                    }
                ]
            },
            {
                "name": "Camera",
                "type": "menu",
                "items": [
                    {
                        "name": "Flip",
                        "type": "menu",
                        "items": [
                            {
                                "name": "Vertically",
                                "type": "option",
                                "function": self.change_cam_flip_v
                            },
                            {
                                "name": "Horizontally",
                                "type": "option",
                                "function": self.change_cam_flip_h
                            }
                        ]
                    }
                ]
            }
        ]

        self.ds = tk.Canvas(self.display, background="gray",
                            highlightthickness=0)

        class ref:
            w = self.monitor_areas[4]
            h = self.monitor_areas[5]

        class cs:
            w = self.wc_width
            h = self.wc_height

        if cs.w > cs.h:
            self.ds_w = int(cs.w * ref.h / cs.h)
            self.ds_h = int(ref.h)
            self.ds.configure(width=self.ds_w, height=self.ds_h)
        else:
            self.ds_w = int(ref.w)
            self.ds_h = int(cs.h * ref.w / cs.w)
            self.ds.configure(width=self.ds_w, height=self.ds_h)

        self.ds.place(x=int(ref.w / 2 - self.ds_w / 2),
                      y=int(ref.h / 2 - self.ds_h / 2))

        self.started = False

        self.registered_events = {}
        self.registered_widgets = []

        self.new_manual_border = True
        self.new_ds_points = True

        generate_menu(self.controller, self.menu)

    def run(self):
        self.controller.after(800, self.loop)
        self.controller.mainloop()

    def update_widgets(self):
        for widget in self.registered_widgets:
            widget.update()

    def update(self):
        self.controller.update()

        self.act_f += 1
        t = time.time()
        if t - self.act_fps_time >= 1:
            self.act_fps_time = t
            self.act_fps = copy.deepcopy(self.act_f)
            self.act_f = 0
        self.controller.title(
            f"MITouch Controller ; {self.wc_width}x{self.wc_height} ; #{self.getParameter('cam_port')} ; {self.fps}FPS ; {self.act_fps}RFPS ; Resized : {self.getParameter('resized')} ; Manual border : {self.getParameter('manual_border')}")

        for event in copy.deepcopy(self.registered_events).values():
            for cursor_index, cursor in enumerate(copy.deepcopy(self.cursor_states).values()):
                x = cursor[1][0]
                y = cursor[1][1]
                state = cursor[0]
                if (x >= event["bbox"][0] and x <= event["bbox"][2]) and (y >= event["bbox"][1] and y <= event["bbox"][3]):
                    if state == None:
                        state = "hover"
                    event[state](x, y, cursor_index)

        if len(FLUX.getValue("run_bundle").strip()):
            runBundle(FLUX.getValue("run_bundle").strip(), self.ds, self.event_register, self.widget_register)
            FLUX.setValue("run_bundle", "")

        self.update_widgets()

        self.controller.update()

    def change_fps(self, factor: int, replace: bool = False):
        factor = copy.copy(factor)
        if not replace:
            pre = copy.copy(self.fps) + factor
        else:
            pre = factor
        if pre >= 1:
            self.fps = pre
        else:
            self.fps = 1
        self.update()

    def calibrate_points(self, img):
        hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        lower1 = np.array([30, 100, 40])  # Green
        upper1 = np.array([80, 255, 255])

        lower4 = np.array([0, 100, 100])  # Blue
        upper4 = np.array([10, 255, 255])

        mask1 = cv2.inRange(hsv_img, lower1, upper1)
        mask4 = cv2.inRange(hsv_img, lower4, upper4)

        contours1, _1 = cv2.findContours(
            mask1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours4, _4 = cv2.findContours(
            mask4, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        overlay_tk_image = ...

        if contours1:
            max_contour = max(contours1, key=cv2.contourArea)
            x1, y1, w, h = cv2.boundingRect(max_contour)

            images = []
            images.append(overlay_tk_image)

        if contours4:
            max_contour = max(contours4, key=cv2.contourArea)
            x4, y4, w, h = cv2.boundingRect(max_contour)

            images = []
            images.append(overlay_tk_image)

        for k, line in enumerate(self.pvw_points):
            try:
                self.preview_canvas.delete(line)
            except Exception as e:
                log("Exception", e)
            self.pvw_points.pop(k)

        if contours1 and contours4:
            self.pvw_points.append(self.preview_canvas.create_text(
                x4, y4, fill="red", text="PointA"))
            self.pvw_points.append(self.preview_canvas.create_text(
                x1, y1, fill="red", text="PointB"))
            self.pvw_points.append(None)
            self.pvw_pointA_x, self.pvw_pointA_y = x4, y4
            self.pvw_pointB_x, self.pvw_pointB_y = x1, y1

    def start(self):
        FLUX.setValue("ds_w", self.ds_w)
        FLUX.setValue("ds_h", self.ds_h)
        FLUX.setValue("ds_points_size", self.getParameter("ds_points_size"))
        runBundle("gui", self.ds, self.event_register, self.widget_register)
        runBundle("menubar", self.ds, self.event_register,
                  self.widget_register)

    def widget_register(self, widget: widget):
        self.registered_widgets.append(widget)

    def event_register(self, type: str, name: str, event_type: str = "click", event_func=void, bbox: tuple = (0, 0, 1, 1)):
        if not name in self.registered_events.keys():
            self.registered_events[name] = {
                "click": void,
                "drag": void,
                "release": void,
                "hover": void,
                "bbox": (0, 0, 1, 1)
            }
        if type == "add":
            self.registered_events[name]["bbox"] = bbox
            self.registered_events[name][event_type] = event_func
        elif type == "del":
            del self.registered_events[name]

    def __drag_pointA(self, event):
        x, y = event.x, event.y
        self.pvw_pointA_x, self.pvw_pointA_y = x, y

    def __drag_pointB(self, event):
        x, y = event.x, event.y
        self.pvw_pointB_x, self.pvw_pointB_y = x, y

    def loop(self):
        self.update()

        if not self.started:
            self.start()
            self.started = True
        if self.cam.isOpened():
            success, img = self.cam.read()
            if success:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                if self.getParameter("resized"):
                    img = cv2.resize(
                        img, (self.controller.winfo_width(), self.controller.winfo_height()))

                if self.getParameter("cam_flip_v"):
                    img = cv2.flip(img, 0)
                if self.getParameter("cam_flip_h"):
                    img = cv2.flip(img, 1)

                if self.getParameter("manual_border"):
                    if self.new_manual_border:
                        for k, line in enumerate(self.pvw_points):
                            self.preview_canvas.delete(line)
                        self.pvw_points = []

                        self.ds.delete(self.ds_pointA)
                        self.ds.delete(self.ds_pointB)

                        pointA_todrag = self.preview_canvas.create_oval(self.pvw_pointA_x - int(self.getParameter("pvw_points_size") / 2), self.pvw_pointA_y - int(self.getParameter(
                            "pvw_points_size") / 2), self.pvw_pointA_x + int(self.getParameter("pvw_points_size") / 2), self.pvw_pointA_y + int(self.getParameter("pvw_points_size") / 2), fill="blue", outline="")

                        pointB_todrag = self.preview_canvas.create_oval(self.pvw_pointB_x - int(self.getParameter("pvw_points_size") / 2), self.pvw_pointB_y - int(self.getParameter(
                            "pvw_points_size") / 2), self.pvw_pointB_x + int(self.getParameter("pvw_points_size") / 2), self.pvw_pointB_y + int(self.getParameter("pvw_points_size") / 2), fill="green", outline="")

                        self.pvw_points += [pointA_todrag, pointB_todrag]

                        self.preview_canvas.tag_bind(
                            pointA_todrag, "<B1-Motion>", self.__drag_pointA)
                        self.preview_canvas.tag_bind(
                            pointB_todrag, "<B1-Motion>", self.__drag_pointB)

                        self.new_manual_border = False
                    else:
                        if len(self.pvw_points) == 2:
                            self.preview_canvas.coords(
                                self.pvw_points[0],
                                self.pvw_pointA_x -
                                int(self.getParameter("pvw_points_size") / 2),
                                self.pvw_pointA_y -
                                int(self.getParameter("pvw_points_size") / 2),
                                self.pvw_pointA_x +
                                int(self.getParameter("pvw_points_size") / 2),
                                self.pvw_pointA_y +
                                int(self.getParameter("pvw_points_size") / 2)
                            )
                            self.preview_canvas.coords(
                                self.pvw_points[1],
                                self.pvw_pointB_x -
                                int(self.getParameter("pvw_points_size") / 2),
                                self.pvw_pointB_y -
                                int(self.getParameter("pvw_points_size") / 2),
                                self.pvw_pointB_x +
                                int(self.getParameter("pvw_points_size") / 2),
                                self.pvw_pointB_y +
                                int(self.getParameter("pvw_points_size") / 2)
                            )
                else:
                    if self.new_ds_points:
                        self.ds_pointA = self.ds.create_rectangle(0, 0, self.getParameter(
                            "ds_points_size"), self.getParameter("ds_points_size"), fill="blue", outline="")
                        self.ds_pointB = self.ds.create_rectangle(self.ds_w - self.getParameter(
                            "ds_points_size"), self.ds_h - self.getParameter("ds_points_size"), self.ds_w, self.ds_h, fill="green", outline="")

                        self.new_ds_points = False
                    self.calibrate_points(img)

                for i_, landmark in enumerate(self.landmarks_canvas):
                    self.ds.delete(landmark)
                    self.landmarks_canvas.pop(i_)

                thumb_landmark = None
                index_landmark = None

                results = self.hands.process(img)

                if results.multi_hand_landmarks:
                    for i_, landmark in enumerate(self.landmarks_canvas):
                        self.ds.delete(landmark)
                        self.landmarks_canvas.pop(i_)
                    for hand_index, hand_landmarks in enumerate(results.multi_hand_landmarks):
                        founded = True
                        hand_index = str(hand_index)
                        if not hand_index in self.cursor_states.keys():
                            self.cursor_states[hand_index] = [None, [0, 0]]
                        for landmark in hand_landmarks.landmark:
                            x = int(landmark.x * img.shape[1])
                            y = int(landmark.y * img.shape[0])
                            converted_x, converted_y = self.convertWebcamPointToDisplay(
                                x, y)

                            if landmark == hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP]:
                                thumb_landmark = (converted_x, converted_y)
                            elif landmark == hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]:
                                index_landmark = (converted_x, converted_y)

                        if thumb_landmark and index_landmark:
                            cursor_state = self.cursor_states[hand_index][0]

                            self.landmarks_canvas.append(self.ds.create_line(
                                thumb_landmark[0], thumb_landmark[1], index_landmark[0], index_landmark[1], fill="white"))
                            dist = max(1, math.dist(
                                thumb_landmark, index_landmark))
                            medX, medY = int((thumb_landmark[0] + index_landmark[0]) / 2), int(
                                (thumb_landmark[1] + index_landmark[1]) / 2)
                            ref = 60
                            wdh = min(int(ref ** 2 / dist), ref)
                            wd = int(wdh / 2)
                            self.cursor_states[hand_index][1] = [medX, medY]
                            self.landmarks_canvas.append(self.ds.create_oval(
                                medX - wd, medY - wd, medX + wd, medY + wd, fill="white", outline=""))
                            if wdh >= ref - self.getParameter("click_sensibility"):
                                self.ds.delete(self.landmarks_canvas[-2])
                                self.ds.itemconfig(
                                    self.landmarks_canvas[-1], fill="#82d6fa")
                                if cursor_state == None or cursor_state == "release":
                                    cursor_state = "click"
                                    self.clicked_at(medX, medY, hand_index)
                                else:
                                    cursor_state = "drag"
                                    self.dragging_at(medX, medY, hand_index)
                            else:
                                if cursor_state == "drag" or cursor_state == "click":
                                    cursor_state = "release"
                                    self.release_at(medX, medY, hand_index)
                                else:
                                    cursor_state = None
                            self.cursor_states[hand_index][0] = cursor_state
                else:
                    cursor_states = {}

                img = ImageTk.PhotoImage(Image.fromarray(img))
                if self.image_on_canvas is None:
                    self.image_on_canvas = self.preview_canvas.create_image(
                        0, 0, anchor=tk.NW, image=img)
                else:
                    self.preview_canvas.itemconfig(
                        self.image_on_canvas, image=img)
                self.preview_canvas.image = img

        self.controller.after(int(1000 / self.fps), self.loop)

    def convertWebcamPointToDisplay(self, x: int, y: int):
        webcam_distance = ((self.pvw_pointB_x - self.pvw_pointA_x)
                           ** 2 + (self.pvw_pointB_y - self.pvw_pointA_y)**2)**0.5

        canvas_distance = ((self.ds_w - self.getParameter("ds_points_size"))
                           ** 2 + (self.ds_h - self.getParameter("ds_points_size"))**2)**0.5

        if webcam_distance == 0:
            webcam_distance = 1

        ratio = canvas_distance / webcam_distance

        converted_x = int((x - self.pvw_pointA_x) * ratio +
                          self.getParameter("ds_points_size"))
        converted_y = int((y - self.pvw_pointA_y) * ratio +
                          self.getParameter("ds_points_size"))

        return converted_x, converted_y

    def convertDisplayPointToWebcam(self, x: int, y: int):
        webcam_distance = ((self.pvw_pointB_x - self.pvw_pointA_x)
                           ** 2 + (self.pvw_pointB_y - self.pvw_pointA_y)**2)**0.5

        canvas_distance = ((self.ds_w - self.getParameter("ds_points_size"))
                           ** 2 + (self.ds_h - self.getParameter("ds_points_size"))**2)**0.5

        ratio = webcam_distance / canvas_distance

        converted_x = int(
            (x - self.getParameter("ds_points_size")) * ratio + self.pvw_pointA_x)
        converted_y = int(
            (y - self.getParameter("ds_points_size")) * ratio + self.pvw_pointA_y)

        return converted_x, converted_y

    def clicked_at(self, x: int, y: int, hand: int = 0):
        pass  # print(f"Clicked at : {x}, {y} #{hand}")

    def dragging_at(self, x: int, y: int, hand: int = 0):
        pass  # print(f"Dragging at : {x}, {y} #{hand}")

    def release_at(self, x: int, y: int, hand: int = 0):
        pass  # print(f"Release at : {x}, {y} #{hand}")

    def change_resized(self):
        self.setParameter("resized", not self.getParameter("resized"))

    def change_border_mode(self):
        self.setParameter(
            "manual_border", not self.getParameter("manual_border"))
        self.new_manual_border = self.new_ds_points = True

    def change_cam_flip_v(self):
        self.setParameter("cam_flip_v", not self.getParameter("cam_flip_v"))

    def change_cam_flip_h(self):
        self.setParameter("cam_flip_h", not self.getParameter("cam_flip_h"))

    def getParameter(self, key: str): return copy.deepcopy(
        self.parameters[key])

    def setParameter(
        self, key: str, value: any): self.parameters[key] = copy.deepcopy(value)
