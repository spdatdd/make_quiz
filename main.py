from libraries_needed import *
from classes_needed import *

class LoginApp(MDApp):
    eternal_data = ListProperty([])
    eternal_refreshing = BooleanProperty()
    eternal_start_idx = 0
    eternal_end_idx = 10
    local_data = ListProperty([])
    local_refreshing = BooleanProperty()
    local_start_idx = 0
    local_end_idx = 30
    user = DictProperty({'username': '', 'password': '', 'avatar': '', 'new_username': '', 'new_password': ''})
    current_directory = os.path.abspath(os.path.dirname(__file__))
    LatexNodes2Text = LatexNodes2Text()
    eternal_list = []
    local_list = []
    temp_local_list = []
    did_exam_list = []
    liked_exam_list = []
    type_exam = 'local'
    load_bai_thi = BooleanProperty(False)
    is_offline = BooleanProperty(False)
    logger = []

    def __init__ (self, **kwargs):
        super().__init__(**kwargs)
        self.screen = Builder.load_file('main.kv')
               
    def build (self):
        # giao diện ứng dụng
        self.theme_cls.theme_style = 'Light'
        self.theme_cls.primary_palette = 'Blue'
        self.theme_cls.accent_palette = 'DeepPurple'
        # đăng ký font name
        LabelBase.register(name='NotoSans', fn_regular='assets/fonts/NotoSans-Regular.ttf')
        LabelBase.register(name='M_PLUS_Rounded_1c', fn_regular='assets/fonts/M_PLUS_Rounded_1c/MPLUSRounded1c-Regular.ttf')
        # cài đặt quản lý màn hình
        self.sm = ScreenManager(transition=FadeTransition(duration=0))
        self.home_screen = BottomNavigation(name='home')
        self.login_screen = LoginScreen(name='login')
        self.register_screen = RegisterScreen(name='register')
        self.sm.add_widget(self.home_screen)
        self.sm.add_widget(self.login_screen)
        self.sm.add_widget(self.register_screen)
        return self.sm

    def on_start (self):
        with open(f"{self.current_directory}/data/user.json", 'r', encoding='utf-8') as json_file:
            self.user = json.load(json_file)
        if len(self.user['username'])>0 and len(self.user['password'])>0:
            self.go_home()
        else:
            self.sm.current = 'login'

    def on_stop (self):
        """Lưu công việc trước khi thoát"""
        print('exit')
        # Đọc file log
        with open(os.path.join(self.current_directory, 'log.txt'), 'r', encoding='utf-8') as file:
            log_cont = file.read()
        # Lưu log
        with open(os.path.join(self.current_directory, 'log.txt'), 'w', encoding='utf-8') as file:
            log = ''
            for e in self.logger:
                log += str(e) + '\n'
            file.write(log_cont+log)
        # Lưu danh sách bài thi đã tạo (chỉnh sửa)
        with open(f"{self.current_directory}/data/file_local_exam.json", 'w', encoding='utf-8') as json_file:
            json.dump(self.local_list, json_file, ensure_ascii=False)
        # Lưu danh sách bài thi online
        with open(f"{self.current_directory}/data/file_eternal_exam.json", 'w', encoding='utf-8') as json_file:
            json.dump(self.eternal_list, json_file, ensure_ascii=False)
        # Lưu danh sách kết quả bài thi đã làm
        with open(f"{self.current_directory}/data/file_save_result_exam.json", 'w', encoding='utf-8') as json_file:
            json.dump(self.did_exam_list, json_file, ensure_ascii=False)
        # Lưu thay đổi trên server
        self.luu_thong_tin_user()
    
    def tolog (self, type, name=''):
        """Ghi log
        """
        self.logger.append(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} {type} {name}')

    def go_home (self):
        """Vào màn hình chính"""
        # Load bài thi đã tạo
        response = self.make_request(
            'https://tieu0luan0tot0nghiep.000webhostapp.com/get_local_exams.php',
            {"username": self.user['username'], "password": self.user['password']},
            'json',
            'post'
        )
        if response!='not available':
            # online 
            if response['message'] == "completed":
                self.local_list = response['localExams']
            else:
                self.tolog('lỗi load local exams ', response['message'])
        else:
            # offline 
            # load danh sách bài thi đã tạo
            with open(f"{self.current_directory}/data/file_local_exam.json", 'r', encoding='utf-8') as json_file:
                self.local_list = json.load(json_file)
        self.temp_local_list = self.local_list
        # Load kết quả bài thi
        response = self.make_request(
            'https://tieu0luan0tot0nghiep.000webhostapp.com/get_results_exam.php',
            {"username": self.user['username'], "password": self.user['password']},
            'json',
            'post'
        )
        if response!='not available':
            # online 
            if response['message'] == "completed":
                self.did_exam_list = response['resultExams']
            else:
                self.tolog('lỗi load result exams ', response['message'])
        else:
            # offline 
            # load danh sách kết quả bài thi đã làm
            with open(f"{self.current_directory}/data/file_save_result_exam.json", 'r', encoding='utf-8') as json_file:
                self.did_exam_list = json.load(json_file)
        self.chu_de_home('All')
        self.sm.current = 'home'   
    
    def logout(self):
        self.user['username']=self.user['new_username']=''
        self.user['password']=self.user['new_password']=''
        self.user['avatar']=self.user['new_avatar']=''
        self.local_list.clear()
        self.did_exam_list.clear()
        with open(f"{self.current_directory}/data/user.json", 'w', encoding='utf-8') as json_file:
            json.dump(self.user, json_file, ensure_ascii=False)
        self.sm.current = 'login'
    
    def is_network_available(self):
        """ 
        Kiểm tra kết nối mạng
            None
        Returns:
            True nếu khả dụng
            False ngược lại
        """
        try:
            # Thực hiện yêu cầu HTTP đơn giản
            urlopen('http://www.google.com', timeout=1)
            return True
        except:
            return False

    def make_request (self, url, data={}, type_result='text', method='get'):
        """Tạo kết nối tới server \n
        Parameters:
            url (str): đường dẫn
            data (Dic): dữ liệu
            type_result (str): text/json
            method (str): post/get
        Returns:
            data/message
        """
        if self.is_network_available():
            try:
                if method=='post':
                    response = requests.post(url, data=data)
                else:
                    response = requests.get(url)
                response.raise_for_status()  # Kiểm tra lỗi HTTP status code
                if type_result=='text':
                    result = response.text
                else:
                    result = response.json()
            except requests.exceptions.HTTPError as errh:
                print(f"HTTP Error: {errh}")
            except requests.exceptions.ConnectionError as errc:
                print(f"Error Connecting: {errc}")
            except requests.exceptions.Timeout as errt:
                print(f"Timeout Error: {errt}")
            except requests.exceptions.RequestException as err:
                print(f"Request Exception: {err}")
            finally:
                return result
        else:
            self.tolog(f"failed {url}", " ")
            return 'not available'

    def show_toast_luu_thong_tin(self, taikhoan, matkhau):
        self.user['new_username'] = taikhoan.text
        self.user['new_password'] = matkhau.text
        toast('Lưu Thành Công')

    def luu_thong_tin_user(self):
        have_update = update_user = update_pw = update_avatar = False
        if len(self.user['new_username']) > 0 and not self.user['username']==self.user['new_username']:
            have_update = update_user = True
        if len(self.user['new_password']) > 0 and not self.user['password']==self.user['new_password']:
            have_update = update_pw = True
        if len(self.user['new_avatar']) > 0 and not self.user['avatar']==self.user['new_avatar']:
            have_update = update_avatar = True
        # URL của endpoint hoặc API để tải lên
        if have_update:
            upload_url = 'https://tieu0luan0tot0nghiep.000webhostapp.com/upload.php'
            data = self.user.copy()
            if len(self.user['new_avatar']) > 0:
                # Đường dẫn đến tệp ảnh bạn muốn tải lên
                image_path = self.user['new_avatar']
                data['new_avatar'] = os.path.basename(data['new_avatar'])
                # Đặt thông tin tệp và các dữ liệu khác cần thiết (nếu có)
                img_extension = os.path.splitext(image_path)[1].replace('.', '')
                files = {'file': (data['new_avatar'], open(image_path, 'rb'), f'image/{img_extension}')}
                # Gửi yêu cầu POST với tệp ảnh
                # response = requests.post(upload_url, files=files)
                response = requests.post(upload_url, files=files, data=data)
            else:
                response = requests.post(upload_url, data=data)
            # Kiểm tra mã trạng thái và hiển thị nội dung phản hồi
            print('Nội dung phản hồi:', response.text)
            if response.text.find("Cập nhật thành công!") != -1:
                if update_user:
                    self.user['username'] = self.user['new_username']
                if update_pw:
                    self.user['password'] = self.user['new_password']
                if update_avatar:
                    self.user['avatar'] = self.user['new_avatar']
                self.user['new_username']=self.user['new_password']=self.user['new_avatar']=''
                with open(f"{self.current_directory}/data/user.json", 'w', encoding='utf-8') as json_file:
                    json.dump(self.user, json_file, ensure_ascii=False)
        
    def eternal_check_pull_refresh(self, view, grid):
        """Check the amount of overscroll to decide if we want to trigger the
        refresh or not.
        """
        view.distance_to_top = (1 - view.scroll_y) * view.scrollable_distance
        max_pixel = dp(200)
        to_relative = max_pixel / (grid.height - view.height)
        if view.scroll_y + to_relative >= 0  or self.eternal_refreshing:
            return
        self.eternal_refresh_data()

    def local_check_pull_refresh(self, view, grid):
        """Check the amount of overscroll to decide if we want to trigger the
        refresh or not.
        """
        view.distance_to_top = (1 - view.scroll_y) * view.scrollable_distance

        max_pixel = dp(200)
        to_relative = max_pixel / (grid.height - view.height)
        if view.scroll_y + to_relative >= 0  or self.local_refreshing:
            return
        
        self.local_refresh_data()

    def eternal_refresh_data(self):
        """ using a Thread to do a potentially long operation without blocking
        the UI """
        def _refresh_data():
            sleep(2)
            if len(self.eternal_list)!=0:
                prepend_data()
        def callback (x):
            print('before: ', x)
            select_data = 'default'
            for data in self.eternal_data:
                if data["selected"]:
                    select_data = data['text']
            print('after: ',select_data)
            # if select_data != 'default' and not self.load_bai_thi:
            #     self.type_exam = 'eternal'
            #     self.lam_bai_thi(select_data)
        @mainthread
        def prepend_data():
            async def generate_card():
                for dt in self.eternal_list[self.eternal_start_idx : self.eternal_end_idx]:
                    await asynckivy.sleep(0)
                    # try:
                    #     id = dt['id']
                    # except Exception as e:
                    #     self.tolog(f'{type(e)} {e}')
                    #     id = -1
                    # else:
                    self.eternal_data.append({
                            "text": dt['ten_bai_thi'],
                            "id": dt['id'],
                            "chu_de": dt['chu_de'],
                            "selected": False,
                            "callback": lambda x: callback(x)
                        })
                self.eternal_refreshing = False
                self.eternal_start_idx = self.eternal_end_idx
                self.eternal_end_idx = self.eternal_end_idx + 30
                if (self.eternal_start_idx > len(self.eternal_list)-1):
                    self.eternal_start_idx = len(self.eternal_list)
                    self.eternal_end_idx = len(self.eternal_list) + 30
            Clock.schedule_once(lambda x: asynckivy.start(generate_card()))
        self.eternal_refreshing = True
        Thread(target=_refresh_data).start()

    def local_refresh_data(self):
        """ using a Thread to do a potentially long operation without blocking
        the UI """  
        def _refresh_data():
            sleep(2)
            if len(self.local_list)!=0:
                prepend_data()
        @mainthread
        def prepend_data():
            async def generate_card():
                for dt in self.local_list[self.local_start_idx : self.local_end_idx]:
                    await asynckivy.sleep(0)
                    try:
                        id = dt['id']
                    except Exception as e:
                        self.tolog(f'{type(e)} {e}')
                        id = -1
                    finally:
                        self.local_data.append({
                            "text": dt['ten_bai_thi'],
                            "id": id,
                            "selected": False,
                            "callback": lambda x: x,
                        })
                self.local_refreshing = False
                self.local_start_idx = self.local_end_idx
                self.local_end_idx = self.local_end_idx + 30
                if (self.local_start_idx > len(self.local_list)-1):
                    self.local_start_idx = len(self.local_list)
                    self.local_end_idx = len(self.local_list) + 30
            Clock.schedule_once(lambda x: asynckivy.start(generate_card()))
        self.local_refreshing = True
        Thread(target=_refresh_data).start()    

    def load_eternal_exam(self):
        temp_list = []
        if self.is_network_available():
            try:
                url = "https://tieu0luan0tot0nghiep.000webhostapp.com/get_external_exam.php"
                response = requests.get(url)
                response.raise_for_status()  # Kiểm tra lỗi HTTP status code
                # Kiểm tra nếu dữ liệu là JSON
                temp_list = response.json()
            except requests.exceptions.HTTPError as errh:
                print(f"HTTP Error: {errh}")
            except requests.exceptions.ConnectionError as errc:
                print(f"Error Connecting: {errc}")
            except requests.exceptions.Timeout as errt:
                print(f"Timeout Error: {errt}")
            except requests.exceptions.RequestException as err:
                print(f"Request Exception: {err}")
        else:
            with open(f"{self.current_directory}/data/file_eternal_exam.json", 'r', encoding='utf-8') as json_file:
                temp_list = json.load(json_file)
        return temp_list

    def chu_de_home(self, text):
        """ Hiển thị các bài thi theo chủ đề ở màn hình home"""
        # Mảng bài thi của user khác
        temp_list = self.load_eternal_exam()
        mang_can_tim = []
        self.eternal_data.clear(), self.eternal_list.clear()
        if text == 'All':
           mang_can_tim = temp_list
        else:
            for dt in temp_list:
                if dt['chu_de'] == text:
                    # self.eternal_list.append(dt)
                    mang_can_tim.append(dt)
        if len(mang_can_tim) > 0:
            self.eternal_start_idx, self.eternal_end_idx = 0, 30
            self.eternal_list = mang_can_tim
            # Cập nhật giao diện
            self.eternal_refresh_data()
        else:
            self.open_snackbar('Không tìm thấy!')

    def danh_sach_bai_thi_home(self):
        """ Hiển thị các bài thi của users đã upload"""
        if len(self.eternal_list) == 0:
            self.eternal_list = self.load_eternal_exam()
        if len(self.eternal_list) != 0 and len(self.eternal_data)==0:
            self.eternal_refresh_data()

    def local_list_on_marked(self, root, segment_button: MDSegmentedButton, segment_item: MDSegmentedButtonItem, marked: bool):
        selected_text = segment_item.text
        if selected_text == 'Đã làm':
            self.bottom_appbar_refresh(root, 'did')
            root.ids.bottom_appbar.action_items = [
                MDActionBottomAppBarButton(icon="play")]
            for button in root.ids.bottom_appbar.action_items:
                icon = button.icon
                if icon == 'play':
                    button.bind(on_release=lambda *arg: self.bottom_appbar_action())
                    break
        if selected_text == 'Đã tạo':
            self.bottom_appbar_refresh(root, 'created')
            root.ids.bottom_appbar.action_items = [
                MDActionBottomAppBarButton(icon="play"),
                MDActionBottomAppBarButton(icon="delete"),
                MDActionBottomAppBarButton(icon="magnify"),
                MDActionBottomAppBarButton(icon="refresh"),
                MDActionBottomAppBarButton(icon="pencil")]
            for button in root.ids.bottom_appbar.action_items:
                icon = button.icon
                if icon == 'play':
                    button.bind(on_release=lambda x: self.bottom_appbar_action())
                if icon == 'delete':
                    button.bind(on_release=lambda x: self.bottom_appbar_delete(root.ids.card_list))
                if icon == 'magnify':
                    button.bind(on_release=lambda x: self.bottom_appbar_search())
                if icon == 'refresh':
                    button.bind(on_release=lambda x: self.bottom_appbar_refresh(root, 'created'))
                if icon == 'pencil':
                    button.bind(on_release=lambda x: self.chinh_sua_bai_thi('mod'))

    def bottom_appbar_refresh(self, root, type):
        self.local_start_idx, self.local_end_idx = 0, 30
        self.local_data.clear()
        if type == 'created':
            if not self.is_network_available():
                with open(f"{self.current_directory}/data/file_local_exam.json", 'r', encoding='utf-8') as json_file:
                    self.local_list = json.load(json_file)
            else:
                self.local_list = self.temp_local_list
        if type == 'did':
            file_save_result_exam = []
            if not self.is_network_available():
                with open(f"{self.current_directory}/data/file_save_result_exam.json", 'r', encoding='utf-8') as json_file:
                    file_save_result_exam = json.load(json_file)
            else:
                file_save_result_exam = self.did_exam_list
                mang_id_bai_thi_ket_qua = [bt['id'] for bt in file_save_result_exam]
                print(self.type_exam)
                print(mang_id_bai_thi_ket_qua)
                if self.type_exam=='eternal':
                    self.local_list = [bt for bt in self.eternal_list if bt['id'] in mang_id_bai_thi_ket_qua]
                else:
                    self.local_list = [bt for bt in self.local_list if bt['id'] in mang_id_bai_thi_ket_qua]
        if len(self.local_list) == 0:
            try:
                root.ids.card_list.data.clear()
            except Exception as e:
                self.tolog(e)
            else:
                root.ids.card_list.refresh_from_data()
                self.local_refreshing = False
                root.ids.refreshLabel.text = ''
        else:
            self.local_refresh_data()

    def bottom_appbar_action(self):
        select_data = 'default'
        for data in self.local_data:
            if data["selected"]:
                select_data = data['text']
        if select_data != 'default':
            self.type_exam = 'local'
            self.lam_bai_thi(select_data)
    
    def bottom_appbar_delete(self, root):
        selected_items = [ (index, data) 
            for index, data in enumerate(self.local_data) 
            if data["selected"]]
        if len(selected_items) > 0:
            def delet_selected_item():
                # Xóa phần tử khỏi danh sách
                self.local_data.pop(selected_items[0][0])
                self.local_list.pop(selected_items[0][0])
                # Cập nhật giao diện
                root.refresh_from_data()
                # # Ghi dữ liệu JSON
                # with open(f"{self.current_directory}/data/file_local_exam.json", 'w', encoding='utf-8') as json_file:
                #     json.dump(self.local_list, json_file, ensure_ascii=False)
                # Gửi yêu cầu xóa
                bai_thi_id = selected_items[0][1]['id']
                ten_bai_thi = selected_items[0][1]['text']
                if bai_thi_id != -1:
                    message = self.make_request(
                        'https://tieu0luan0tot0nghiep.000webhostapp.com/delete_a_exam.php',
                        {"ten_bai_thi": ten_bai_thi, "bai_thi_id":bai_thi_id, "user": self.user['username'], "password": self.user['password']},
                        'text',
                        'post'
                    )
                    if message not in ['completed', 'Không có bài thi!']:
                        self.tolog("failed_deleted_exam at button bottom delete", selected_items[0][1]['text']+' '+message)
                dialog.dismiss()
                self.open_snackbar('Xóa bài thi thành công!')
            dialog = MDDialog(
                text='Bạn có chắc muốn xóa bài thi này?',
                buttons=[
                    MDFlatButton(
                        text="Không",
                        theme_text_color="Error",
                        on_release=lambda x: dialog.dismiss()
                    ),
                    MDFlatButton(
                        text="Đồng ý",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release=lambda x: delet_selected_item()
                    )
                ],
            )
            dialog.open()

    def bottom_appbar_search(self):
        def search_action(content):
            with open(f"{self.current_directory}/data/file_local_exam.json", 'r', encoding='utf-8') as json_file:
                data_local_exam = json.load(json_file)

            array_correct = []
            for data in data_local_exam: 
                if data["ten_bai_thi"].find(content) != -1:
                    array_correct.append(data)

            if len(array_correct) > 0:
                self.local_start_idx, self.local_end_idx = 0, 30
                self.local_data.clear(), self.local_list.clear()
                self.local_list = array_correct
                self.local_refresh_data()

            else:
                self.open_snackbar('Không tìm thấy!')

            dialog.dismiss()
        
        content = Custom_content()
        dialog = MDDialog(
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="Không",
                    theme_text_color="Error",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDFlatButton(
                    text="Đồng ý",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release=lambda x: search_action(content.text)
                )
            ],
        )
        dialog.open()

    def snackbar_close(self, *args):
        self.snackbar.dismiss()

    def open_snackbar(self, txt):
        self.snackbar = MDSnackbar(
            MDLabel(
                text=txt,
                theme_text_color="Custom",
                text_color="#393231",
            ),
            MDSnackbarCloseButton(
                icon="close",
                theme_text_color="Custom",
                text_color="#8E353C",
                _no_ripple_effect=True,
                on_release=self.snackbar_close,
            ),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            size_hint_x=.8,
            md_bg_color="#E8D8D7",
        )
        self.snackbar.open()

    def exit_exam(self, root):
        def handle(root, dialog):
            dialog.dismiss()
            self.sm.remove_widget(root)

        dialog = MDDialog(
            text='Bạn muốn kết thúc làm bài ?',
            buttons=[
                MDFlatButton(
                    text="Không",
                    theme_text_color="Error",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDFlatButton(
                    text="Đồng ý",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release=lambda x: handle(root, dialog)
                )
            ],
        )
        dialog.open()

    def chinh_sua_bai_thi(self, type):
        Exam_screen = CreateExamScreen(name='create_exam')
        Exam_screen.mode = type
        if type == 'mod':
            select_data = ''
            for data in self.local_data:
                if data["selected"]:
                    select_data = data['text']
            if len(select_data)>0:
                # Biểu tượng load
                self.load_bai_thi = True
                # Đặt giá trị cho widget chỉnh sửa bài thi
                try:
                    selected_exam_in_data = [dl for dl in self.local_list if dl['ten_bai_thi']==select_data]
                except:
                    print(self.local_list)
                else:
                    Exam_screen.ids.TenBaiThi.text = selected_exam_in_data[0]['ten_bai_thi']
                    Exam_screen.ids.ChuDe.text = selected_exam_in_data[0]['chu_de']
                    # Lấy danh sách câu hỏi
                    array_ques = selected_exam_in_data[0]['danh_sach_cau_hoi']
                    # array_ques.reverse()
                    async def gennerate_data():
                        for i in range(len(array_ques)):
                            await asynckivy.sleep(0)
                            ques = Question()
                            ques.ids.CauHoi.text = self.LatexNodes2Text.latex_to_text(array_ques[i]['cau_hoi'])
                            Exam_screen.ids.Container.add_widget(ques)
                            # array_ques[i]['dap_an'].reverse()
                            if len( array_ques[i]['dap_an']) > 0:
                                for dt in array_ques[i]['dap_an']:
                                    choice = Choice()
                                    choice.ids.CauTraLoiDapAn.text = self.LatexNodes2Text.latex_to_text(dt)
                                    if dt in array_ques[i]['dap_an_9_xac']:
                                        choice.ids.Dung.active = True
                                    Exam_screen.ids.Container.add_widget(choice)
                            else:
                                think_choice  = YourThink()
                                Exam_screen.ids.Container.add_widget(think_choice)
                        self.sm.add_widget(Exam_screen)
                        self.sm.current = 'create_exam'
                        self.load_bai_thi = False
                    Clock.schedule_once(lambda x: asynckivy.start(gennerate_data()))
        if type=='add':
            self.sm.add_widget(Exam_screen)
            self.sm.current = 'create_exam'

    def exit_man_hinh_ket_qua(self, man_hinh_kq, *args):
        if self.sm.has_screen('xem_ket_qua_chi_tiet'):
            self.sm.remove_widget(self.sm.get_screen('xem_ket_qua_chi_tiet'))
        self.sm.remove_widget(man_hinh_kq)

    def xem_chi_tiet_ket_qua_thi(self, ten_bai_thi):
        if self.sm.has_screen('xem_ket_qua_chi_tiet'):
            self.sm.current = 'xem_ket_qua_chi_tiet'
        else:
            bai_thi_can_tim = []
            ket_qua_bai_thi = []
            if self.type_exam == 'local':
                data_exam_list = self.local_list
            if self.type_exam == 'eternal':
                data_exam_list = self.eternal_list
            for bai_thi in data_exam_list:
                if bai_thi['ten_bai_thi'] == ten_bai_thi:
                    bai_thi_can_tim = bai_thi
            for ket_qua in self.did_exam_list:
                if ket_qua['ten_bai_thi'] == ten_bai_thi:
                    ket_qua_bai_thi = ket_qua
            Container = ManHinhChiTietKetQua(name='xem_ket_qua_chi_tiet')
            self.sm.add_widget(Container)
            tong_cau_hoi = len(bai_thi_can_tim['danh_sach_cau_hoi'])
            Container.tong_cau_hoi = len(bai_thi_can_tim['danh_sach_cau_hoi'])
            # bai_thi_can_tim['danh_sach_cau_hoi'].reverse()
            for i in range(tong_cau_hoi):
                trang_thi = TrangThi()
                path_media = bai_thi_can_tim['danh_sach_cau_hoi'][i]['path_media']
                if len(path_media) > 0:
                    extension_media = os.path.splitext(path_media)[1]
                    if extension_media in ['.jpeg', '.png']:
                        img = FitImage()
                        img.radius = [0, 0, '10dp', '10dp']
                        img.source = path_media
                        trang_thi.ids.Media.add_widget(img)
                    if extension_media in ['.mp3', '.wav', '.flac', '.aac', '.m4a', '.aiff', '.wma', '.pcm']:
                        audioMedia = AudioExam()
                        audioMedia.audio = SoundLoader.load(path_media)
                        audioMedia.ids.progress_bar.max = audioMedia.audio.length
                        audioMedia.path_txt = path_media
                        audioMedia.position_progress = 0
                        audioMedia.ids.audio.icon = 'play'
                        trang_thi.ids.Media.add_widget(audioMedia)
                    if extension_media in ['.mp4', '.avi', '.mkv', '.wmv', '.flv', '.mov', '.webm', '.ogg', '.3gp', '.3g2', '.swf']:
                        videoMedia = VideoPlayer(
                            source = path_media,
                            options = {'allow_stretch': True}
                        )
                        trang_thi.ids.Media.add_widget(videoMedia)
                trang_thi.ids.CauHoi.text = self.LatexNodes2Text.latex_to_text(bai_thi_can_tim['danh_sach_cau_hoi'][i]['cau_hoi'])
                if len(bai_thi_can_tim['danh_sach_cau_hoi'][i]['dap_an']) > 0:
                    # bai_thi_can_tim['danh_sach_cau_hoi'][i]['dap_an'].reverse()
                    dung = False
                    if ket_qua_bai_thi['danh_sach_cau_hoi'][i]['dap_an'] == ket_qua_bai_thi['danh_sach_cau_hoi'][i]['dap_an_chinh_xac']:
                        dung = True
                    for dap_an in bai_thi_can_tim['danh_sach_cau_hoi'][i]['dap_an']:
                        dap_an_exam = DapAnExam()
                        dap_an = self.LatexNodes2Text.latex_to_text(dap_an).replace('\xa0', ' ')
                        if dap_an in ket_qua_bai_thi['danh_sach_cau_hoi'][i]['dap_an'] and dung:
                            # màu tím thể hiện chọn chính xác
                            dap_an_exam.md_bg_color = self.theme_cls.accent_dark
                            dap_an_exam.ids.Dung.active = True
                        if dap_an in ket_qua_bai_thi['danh_sach_cau_hoi'][i]['dap_an'] and not dung: 
                            # màu đỏ thể hiện chọn sai
                            dap_an_exam.md_bg_color = [1, 0, 0, 1]
                            dap_an_exam.ids.Dung.active = True
                        if dap_an in ket_qua_bai_thi['danh_sach_cau_hoi'][i]['dap_an_chinh_xac']:
                            # màu tím thể hiện đáp án đúng 
                            dap_an_exam.md_bg_color = self.theme_cls.accent_dark
                        dap_an_exam.ids.CauTraLoiDapAn.text = self.LatexNodes2Text.latex_to_text(dap_an)
                        trang_thi.ids.DapAn.add_widget(dap_an_exam)
                if len(bai_thi_can_tim['danh_sach_cau_hoi'][i]['dap_an']) == 0:
                    dap_an_exam = DapAnDienExam()
                    trang_thi.ids.DapAn.add_widget(dap_an_exam)
                Container.ids.Container.add_widget(trang_thi)
            self.sm.current = 'xem_ket_qua_chi_tiet'

    def finish_exam(self, root):
        def ghi_nhan_ket_qua(root):
            bai_thi = root.ids.Container.slides
            cau_hoi = {"cau_hoi": "",
                        "dap_an": [],
                        "dap_an_chinh_xac": []}
            ket_qua = {"ten_bai_thi": root.name_exam,
                        "ket_qua": "",
                        "id": 0,
                        "danh_sach_cau_hoi": []}
            # # Lấy bài thi tương ứng
            # for et_exam in self.eternal_list:
            #     if et_exam['ten_bai_thi']==root.name_exam:
            #         exactly_exam_in_eternal = et_exam
            # # Lấy id bài thi
            # ket_qua['id'] = exactly_exam_in_eternal['id']
            tong_cau = len(bai_thi)
            tong_cau_dung = 0
            # bai_thi.reverse()
            for cau in bai_thi:
                dap_an_9_xac = []
                for c in cau.dap_an_chinh_xac:
                    c = self.LatexNodes2Text.latex_to_text(c).replace('\xa0', ' ')
                    dap_an_9_xac.append(c)
                cau_hoi['dap_an_chinh_xac'] = dap_an_9_xac
                cau_hoi['id'] = cau.id_cau_hoi
                cau_hoi['cau_hoi'] = cau.ids.CauHoi.text.replace('\xa0', ' ')
                for dap_an in cau.ids.DapAn.children:
                    if ('Dung' in dap_an.ids and dap_an.ids.Dung.active == True) or 'Dung' not in dap_an.ids:
                        cau_hoi['dap_an'].append(dap_an.ids.CauTraLoiDapAn.text.replace('\xa0', ' '))
                ket_qua['danh_sach_cau_hoi'].append(cau_hoi.copy())
                if cau_hoi['dap_an_chinh_xac'] == cau_hoi['dap_an'] or len(cau_hoi['dap_an_chinh_xac'])==0:
                    tong_cau_dung = tong_cau_dung + 1
                cau_hoi['cau_hoi'] = ''
                cau_hoi['dap_an'] = []
                cau_hoi['dap_an_chinh_xac'] = []
            ket_qua['ket_qua'] = f'{tong_cau_dung}/{tong_cau}'
            da_ton_tai_ket_qua_thi = False
            # Lấy id bài thi
            if self.type_exam=='local':
                data = [data for data in self.local_data if data['selected']][0]
            else:
                data = [data for data in self.eternal_data if data['selected']][0]
            ket_qua['id'] = data['id']
            # Kiểm tra nếu kết quả đã có thì cập nhật kết quả mới
            for idx, result in enumerate(self.did_exam_list):
                if result['id'] == ket_qua['id'] and result['ten_bai_thi'] == ket_qua['ten_bai_thi']:
                    da_ton_tai_ket_qua_thi = True
                    # diem_cu = int((result['ket_qua'].split('/'))[0])
                    # diem_moi = int((ket_qua['ket_qua'].split('/'))[0])
                    # if diem_cu < diem_moi:
                    # result['ket_qua'] = ket_qua['ket_qua']
                    # result['danh_sach_cau_hoi'] = ket_qua['danh_sach_cau_hoi']
                    self.did_exam_list[idx] = ket_qua
                    break
            # Nếu chưa có kết quả cho bài thi này thì thêm vào danh sách đã làm
            if not da_ton_tai_ket_qua_thi:
                self.did_exam_list.append(ket_qua)
            # with open(f"{self.current_directory}/file_save_result_exam.json", 'w', encoding='utf-8') as json_file:
            #     json.dump(self.did_exam_list, json_file, ensure_ascii=False)
            # Lưu kết quả lên server
            message = self.make_request(
                'https://tieu0luan0tot0nghiep.000webhostapp.com/create_a_result.php',
                {"data": json.dumps(ket_qua), "user": self.user['username'], "password": self.user['password']},
                'text',
                'post'
            )
            message = message.strip()
            if message != 'completed':
                ten_bai_thi = ket_qua['ten_bai_thi']
                id = ket_qua['id']
                self.tolog('Failed add result', f'{id} {ten_bai_thi} {message}')
            # Đóng dialog
            dialog.dismiss()
            man_hinh_ket_qua = ManHinhKetQua(name="ket_qua_exam")
            man_hinh_ket_qua.ten_bai_thi = root.name_exam
            man_hinh_ket_qua.ids.ket_qua.text = ket_qua['ket_qua']
            self.sm.remove_widget(root)
            self.sm.add_widget(man_hinh_ket_qua)
            self.sm.current = 'ket_qua_exam'
        dialog = MDDialog(
            text='Bạn có chắc muốn kết thúc?',
            buttons=[
                MDFlatButton(
                    text="Không",
                    theme_text_color="Error",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDFlatButton(
                    text="Đồng ý",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release=lambda x: ghi_nhan_ket_qua(root)
                )
            ],
        )
        dialog.open()

    def lam_bai_thi(self, ten_bai_thi):
        self.load_bai_thi = True
        bai_thi_can_tim = []
        # Xác định loại bài thi cục bộ hay ngoại tuyến
        if self.type_exam == 'local':
            list_data_exam = self.local_list
        if self.type_exam == 'eternal':
            list_data_exam = self.eternal_list
        # Tìm bài thi đã chọn
        for bai_thi in list_data_exam:
            if bai_thi['ten_bai_thi'] == ten_bai_thi:
                bai_thi_can_tim = bai_thi
        # Tạo widget làm bài thi
        Container = DoExam(name='lam_bai_thi')
        Container.name_exam = bai_thi_can_tim['ten_bai_thi']
        self.sm.add_widget(Container)
        Container.tong_cau_hoi = len(bai_thi_can_tim['danh_sach_cau_hoi'])
        # bai_thi_can_tim['danh_sach_cau_hoi'].reverse()
        # Load các câu hỏi
        async def gennerate_data():
            for cau in bai_thi_can_tim['danh_sach_cau_hoi']:
                await asynckivy.sleep(0)
                trang_thi = TrangThi()
                try:
                    id_cau_hoi = cau['id']
                except Exception as e:
                    id_cau_hoi = -1
                finally:
                    trang_thi.id_cau_hoi = id_cau_hoi
                path_media = cau['path_media']
                if len(path_media) > 0:
                    extension_media = os.path.splitext(path_media)[1]
                    if extension_media in ['.jpeg', '.png']:
                        img = FitImage()
                        img.radius = [0, 0, '10dp', '10dp']
                        img.source = path_media
                        trang_thi.ids.Media.add_widget(img)
                    if extension_media in ['.mp3', '.wav', '.flac', '.aac', '.m4a', '.aiff', '.wma', '.pcm']:
                        audioMedia = AudioExam()
                        audioMedia.audio = SoundLoader.load(path_media)
                        audioMedia.ids.progress_bar.max = audioMedia.audio.length
                        audioMedia.path_txt = path_media
                        audioMedia.position_progress = 0
                        audioMedia.ids.audio.icon = 'play'
                        trang_thi.ids.Media.add_widget(audioMedia)
                    if extension_media in ['.mp4', '.avi', '.mkv', '.wmv', '.flv', '.mov', '.webm', '.ogg', '.3gp', '.3g2', '.swf']:
                        videoMedia = VideoPlayer(
                            source = path_media,
                            options = {'allow_stretch': True}
                        )
                        trang_thi.ids.Media.add_widget(videoMedia)
                trang_thi.ids.CauHoi.text = self.LatexNodes2Text.latex_to_text(cau['cau_hoi'])
                if len(cau['dap_an']) > 0:
                    try:
                        for c in cau['dap_an_9_xac']:
                            c = self.LatexNodes2Text.latex_to_text(c)
                        trang_thi.dap_an_chinh_xac = cau['dap_an_9_xac']
                    except KeyError:
                        # KeyError == 'dap_an_9_xac'
                        trang_thi.dap_an_chinh_xac = []
                    # cau['dap_an'].reverse()
                    for dap_an in cau['dap_an']:
                        dap_an_exam = DapAnExam()
                        dap_an_exam.ids.CauTraLoiDapAn.text = self.LatexNodes2Text.latex_to_text(dap_an) 
                        trang_thi.ids.DapAn.add_widget(dap_an_exam)
                if len(cau['dap_an']) == 0:
                    dap_an_exam = DapAnDienExam()
                    trang_thi.ids.DapAn.add_widget(dap_an_exam)
                Container.ids.Container.add_widget(trang_thi)
            # Container.ids.Time.text = f"{bai_thi_can_tim[0]['thoi_gian_lam_bai']}:00"
            # self.current_lock = Clock.schedule_interval(partial(self.thoi_gian_lam_bai, Container, bai_thi_can_tim[0]['thoi_gian_lam_bai']), 1)
            self.sm.current = 'lam_bai_thi'
            self.load_bai_thi = False
        Clock.schedule_once(lambda x: asynckivy.start(gennerate_data()))

    def thoi_gian_lam_bai(self, root, time, *arg):
        time_str = root.ids.Time.text
        minute = int(time_str.split(":")[0])
        second = int(time_str.split(":")[1])
        if minute >= 0:
            if second >= 0:
                root.ids.Time.text = f"{minute}:{second-1}"
                if second == 0:
                    root.ids.Time.text = f"{minute-1}:{59}"

    def exit_create_exam(self, root):
        self.sm.remove_widget(root)

    def lam_moi_trang_tao_bai_thi(self, root):
        def clear_container():
            root.ids.ChuDe.text = 'Chủ đề'
            root.ids.LoaiCauHoi.text = 'Loại câu hỏi'
            root.ids.TenBaiThi.text = ''
            root.ids.Container.clear_widgets()
            dialog.dismiss()
        
        dialog = MDDialog(
            text='Bạn có chắc muốn xóa toàn bộ nội dung hiện tại?',
            buttons=[
                MDFlatButton(
                    text="Không",
                    theme_text_color="Error",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDFlatButton(
                    text="Đồng ý",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release=lambda x: clear_container()
                )
            ],
        )
        dialog.open()
    
    def luu_bai_thi(self, Container, TenBaiThi, ChuDe, mode):
        def Save_exam():
            QuestList = []
            q = {
                'cau_hoi': "",
                'dap_an': [],
                'path_media': "",
                'dap_an_9_xac': [],
                }
            for w in Container:
                for id in w.ids:
                    if id == 'Dung':
                        temp_str = w.ids.CauTraLoiDapAn.text
                        q['dap_an'].append(temp_str)
                        if w.ids.Dung.state == 'down':
                            q['dap_an_9_xac'].append(temp_str)
                    if id=='img':
                        q['path_media'] = w.ids[id].source
                    if id=='vid':
                        q['path_media'] = w.ids[id].source
                    if id=='audio':
                        q['path_media'] = w.path_txt
                    if id=='CauHoi':
                        q['cau_hoi'] = w.ids[id].text
                        QuestList.append(q.copy())
                        q['dap_an'] = []
                        q['path_media'] = ''
                        q['dap_an_9_xac'] = []        
            QuestList.reverse()
            exam = {
                "ten_bai_thi" : TenBaiThi,
                "chu_de": ChuDe,
                "danh_sach_cau_hoi": QuestList            
            }
            if mode == 'add':
                response = self.make_request(
                            'https://tieu0luan0tot0nghiep.000webhostapp.com/create_a_exam.php',
                            {"data": json.dumps(exam.copy()), "user": self.user['username'], "password": self.user['password']},
                            'json',
                            'post'
                        )
                if response!='not available':
                    # online 
                    response_message = response['message'].strip()
                    if response_message=='compeleted':
                        self.local_list.append(response['data'])
                    else:
                        self.tolog("failed_add_exam", exam['ten_bai_thi']+' '+response_message)
                else:
                    # offline 
                    self.local_list.append(exam)
            else:
                # Chưa lưu log cho bài thi chỉnh sửa khi mất kết nối mạng
                message = self.make_request(
                    'https://tieu0luan0tot0nghiep.000webhostapp.com/delete_a_exam.php',
                    {"ten_bai_thi": exam['ten_bai_thi'], "user": self.user['username'], "password": self.user['password']},
                    'text',
                    'post'
                )
                if message=='completed' or 'Không có bài thi!':
                    response = self.make_request(
                            'https://tieu0luan0tot0nghiep.000webhostapp.com/create_a_exam.php',
                            {"data": json.dumps(exam.copy()), "user": self.user['username'], "password": self.user['password']},
                            'json',
                            'post'
                        )
                    if response!='not available':
                        # online 
                        response_message = response['message'].strip()
                        if response_message=='compeleted':
                            for index, dl in enumerate(self.local_list):
                                if dl['ten_bai_thi'] == TenBaiThi:
                                    self.local_list[index] = response['data']
                        else:
                            self.tolog("failed_add_exam", exam['ten_bai_thi']+' '+response_message)
                    else:
                        # offline 
                        for index, dl in enumerate(self.local_list):
                            if dl['ten_bai_thi'] == TenBaiThi:
                                self.local_list[index] = exam
                        self.tolog("failed_add_exam online", exam['ten_bai_thi'])
                else:
                    self.tolog("failed_deleted_exam", exam['ten_bai_thi']+' '+message)
            dialog.dismiss()
            self.open_snackbar('Lưu bài thi thành công!')
        dialog = MDDialog(
            text='Bạn có chắc muốn lưu bài thi này?',
            buttons=[
                MDFlatButton(
                    text="Không",
                    theme_text_color="Error",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDFlatButton(
                    text="Đồng ý",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release=lambda x: Save_exam()
                )
            ],
        )
        if ChuDe == 'Chủ đề':
            toast('Vui lòng xác định chủ đề của bài thi!')
        elif TenBaiThi == '':
            toast('Vui lòng nhập tên của bài thi!')
        elif len(Container)==0:
            toast('Không thể lưu bài thi không có nội dung!')
        else: dialog.open()

    def set_loai_cau_hoi(self, text__item, root):
        root.ids.LoaiCauHoi.text = text__item
        self.menu.dismiss()
     
    def set_chu_de(self, text__item, root):
        root.ids.ChuDe.text = text__item
        self.menu.dismiss()

    def add_loai_cau_hoi(self, root):
        menu_items = [
            {
                "height": dp(56),
                "text": f"{item}",
                "on_release": lambda x=f"{item}": self.set_loai_cau_hoi(x, root),
            } for i, item in enumerate(['Trả lời ngắn', 'Chọn đáp án'])]
        self.menu = MDDropdownMenu(
            caller=root.ids.LoaiCauHoi,
            items=menu_items,
            width_mult=4,
        )
        self.menu.check_position_caller = (None, None, None)
        self.menu.open()

    def add_chu_de(self, root):
        menu_items = [
            {
                "height": dp(56),
                "text": f"{item}",
                "on_release": lambda x=f"{item}": self.set_chu_de(x, root),
            } for i, item in enumerate([
                'Lịch sử', 'Tin học', 'Địa lí', 'Công nghệ', 'Ngữ văn', 'Quốc phòng an ninh',
                'Công dân', 'Vật lí', 'Tự nhiên và xã hội', 'Mĩ thuật', 'Kinh tế pháp luật',
                'Tiếng việt', 'Sinh học', 'Hoạt động trải nghiệm', 'Âm nhạc', 'Giáo dục công dân',
                'Tiếng Anh', 'Khoa học', 'Toán', 'Hóa học', 'Đạo đức', 'Giải trí', 'Không có !'
                ])]
        self.menu = MDDropdownMenu(
            caller=root.ids.ChuDe,
            items=menu_items,
            position="bottom",
            width_mult=4,
        )
        # self.menu.check_position_caller = (None, None, None)
        self.menu.open()

    def add_choice_input(self, root):
        CauHoi = root.ids.LoaiCauHoi.text
        if CauHoi == 'Chọn đáp án':
            root.ids.Container.add_widget(Choice())
        elif CauHoi == 'Trả lời ngắn':
            root.ids.Container.add_widget(YourThink())
        else:
            toast('Vui lòng chọn loại câu hỏi !')

    def add_question(self, root):
        root.ids.Container.add_widget(Question())

    def start_audio(self, root):
        audioIcon = root.ids.audio.icon
        if audioIcon == 'play':
            root.ids.audio.icon = 'pause'
            root.audio.play()
            root.audio.seek(root.position_progress)
            self.progress_clock = Clock.schedule_interval(partial(self.update_progress_audio, root), 1)
        else:
            self.stop_audio(root)

    def stop_audio(self, root, *arg):
        root.ids.audio.icon = 'play'
        if hasattr(self, 'progress_clock'):
            self.progress_clock.cancel()
            root.audio.stop()

    def delete_audio(self, root):
        if root.audio is not None and root.audio.state == 'play':
            root.audio.stop()
            root.audio.unload()

    def update_progress_audio(self, root, *arg):
        if root.ids.progress_bar.value < root.audio.length:
            root.ids.progress_bar.value = root.audio.get_pos()
            root.position_progress = root.audio.get_pos()
        if root.audio.state == 'stop':
            self.progress_clock.cancel()
            root.ids.progress_bar.value =0
            root.ids.audio.icon = 'play'

    def file_manager_open(self, root, type):
        on_selection_with_params = partial(self.select_path, root, type)
        filechooser.open_file(on_selection=on_selection_with_params)

    def select_path(self, root, type, selection):
        if len(selection) >= 1:
            def update_ui(*args):
                path = selection[0]
                _, file_extension = os.path.splitext(path)
                if type=='tao_bai_thi':
                    if file_extension in ['.jpg', '.png']:
                        imageMedia = ImageMedia()
                        imageMedia.ids.img.source = path
                        root.ids.Container.add_widget(imageMedia)
                    if file_extension in ['.mp4', '.avi', '.mkv', '.wmv', '.flv', '.mov', '.webm', '.ogg', '.3gp', '.3g2', '.swf']:
                        videoMedia = VideoMedia()
                        videoMedia.ids.vid.source = path
                        root.ids.Container.add_widget(videoMedia)
                    if file_extension in ['.mp3', '.wav', '.flac', '.aac', '.m4a', '.aiff', '.wma', '.pcm']:
                        audioMedia = AudioMedia()
                        audioMedia.audio = SoundLoader.load(path)
                        audioMedia.ids.progress_bar.max = audioMedia.audio.length
                        audioMedia.path_txt = path
                        audioMedia.position_progress = 0
                        audioMedia.ids.audio.icon = 'play'
                        root.ids.Container.add_widget(audioMedia)
                if type=='doi_anh_dai_dien':
                    if file_extension in ['.jpg', '.png', '.jpeg']:
                        root.ids.img.source = path
                        self.user['new_avatar'] = path
            Clock.schedule_once(update_ui)

    def exit_manager(self, *args):
        '''Called when the user reaches the root of the directory tree.'''
        self.file_manager.close()

    def login_regist_request(self, type, username, password):
        data = {"username": username, "password": password}
        img_extension = ''
        #Lấy avatar:
        if type=='login.php':
            url = f"https://tieu0luan0tot0nghiep.000webhostapp.com/get_avatar.php"
            response = requests.post(url, data=data)
            message = response.text
            # Kiểm tra xem yêu cầu có thành công không (mã trạng thái 200)
            if response.status_code == 200:
                content_type = [value for key, value in response.headers.items() if key == 'Content-Type'][0]
                # Đặt tên file và lưu hình ảnh
                if content_type.find('jpeg')!=-1:
                    img_extension = '.jpeg'
                if content_type.find('jpg')!=-1:
                    img_extension = '.jpg'
                if content_type.find('png')!=-1:
                    img_extension = '.png'
                if len(img_extension)>0:
                    self.user['avatar'] = os.path.join( self.current_directory, 'assets', 'images', f'avatar{img_extension}')
                    with open(self.user['avatar'], 'wb') as image_file:
                        image_file.write(response.content)
        #Lấy thông tin đăng nhập
        url = f"https://tieu0luan0tot0nghiep.000webhostapp.com/{type}"
        response = requests.post(url, data=data)
        message = response.text
        # result = response.json()
        # Kiểm tra xem yêu cầu có thành công không (mã trạng thái 200)
        if response.status_code == 200:
            if message in ["Đăng nhập thành công", "Đăng ký thành công"]:
                self.user['username'] = username
                self.user['password'] = password
                # lưu nội dung home
                with open(f"{self.current_directory}/data/user.json", 'w', encoding='utf-8') as json_file:
                    json.dump(self.user, json_file, ensure_ascii=False)
                Clock.schedule_once(lambda x: self.go_home(), 2)
            toast(message)

    def login(self, username, password):
        valid = True
        # ký tự hợp lệ
        pattern = re.compile(r'^[a-zA-Z0-9_]+$')
        if not pattern.match(username):
            toast('Tài khoản không hợp lệ!')
            valid = False
        if not pattern.match(password):
            toast('Mật khẩu không hợp lệ!')
            valid = False
        if valid: 
            self.login_regist_request('login.php', username, password)

    def register(self, username, password, re_password):
        valid = True
        # ký tự hợp lệ
        pattern = re.compile(r'^[a-zA-Z0-9_]+$')
        if len(username) < 8:
            toast('ten nho hon 8')
            valid = False
        if len(password) < 8:
            toast('mk nho hon 8')
            valid = False
        if len(re_password) < 8:
            toast('rmk nho hon 8')
            valid = False
        if not (len(username)<8 and len(password)<8 and len(re_password)<8):
            if not pattern.match(username):
                toast('t ko hop le')
                valid = False
            if not pattern.match(password):
                toast('mk ko hop le')
                valid = False
            if not pattern.match(re_password):
                toast('rmk ko hop le')
                valid = False
        # ít nhất một ký tự số
        pattern = re.compile(r'\d')
        if not (len(username)<8 and len(password)<8 and len(re_password)<8):
            if not (pattern.match(username) and pattern.match(password) and pattern.match(re_password)):
                if not pattern.search(password):
                    toast('chua it nhat mot so')
                    valid = False
                if password != re_password:
                    toast('mk khong khop')
                    valid = False
        if valid: 
            self.login_regist_request('register.php', username, password)

if __name__ == '__main__':
    LoginApp().run()
