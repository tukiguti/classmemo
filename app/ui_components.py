import customtkinter as ctk
from tkinter import messagebox
from tkcalendar import Calendar
from event_handlers import EventHandlers
from database import Database
from datetime import datetime, timedelta

class App(ctk.CTkFrame):
    def __init__(self, master):
        print("Initializing App")
        super().__init__(master)
        self.pack(fill="both", expand=True)  # この行を追加
        print("App initialized")
        self.master = master
        self.root = master 
        self.master.title("学習管理システム")
        self.master.geometry("1024x768")
        
        self.db = Database()
        self.event_handlers = EventHandlers(self)
        self.current_user = None

        self.create_widgets()
        self.show_login_register_screen()  # この行を追加

        self.master.update()
        self.master.deiconify()
        print("Window should be visible now")

    def create_widgets(self):
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y", padx=20, pady=20)

        self.main_area = ctk.CTkFrame(self)
        self.main_area.pack(side="right", fill="both", expand=True, padx=20, pady=20)

    def show_login_register_screen(self):
        self.clear_sidebar()
        self.clear_main_area()
        ctk.CTkButton(self.sidebar, text="ログイン", command=self.show_login_window).pack(pady=10)
        ctk.CTkButton(self.sidebar, text="ユーザー登録", command=self.show_register_window).pack(pady=10)

    def show_login_window(self):
        self.clear_main_area()
        ctk.CTkLabel(self.main_area, text="メールアドレス:").pack(pady=5)
        self.email_entry = ctk.CTkEntry(self.main_area)
        self.email_entry.pack(pady=5)
        ctk.CTkLabel(self.main_area, text="パスワード:").pack(pady=5)
        self.password_entry = ctk.CTkEntry(self.main_area, show="*")
        self.password_entry.pack(pady=5)
        ctk.CTkButton(self.main_area, text="ログイン", command=self.event_handlers.login_user).pack(pady=10)

    def show_register_window(self):
        self.clear_main_area()
        ctk.CTkLabel(self.main_area, text="名前:").pack(pady=5)
        self.name_entry = ctk.CTkEntry(self.main_area)
        self.name_entry.pack(pady=5)
        ctk.CTkLabel(self.main_area, text="メールアドレス:").pack(pady=5)
        self.email_entry = ctk.CTkEntry(self.main_area)
        self.email_entry.pack(pady=5)
        ctk.CTkLabel(self.main_area, text="パスワード:").pack(pady=5)
        self.password_entry = ctk.CTkEntry(self.main_area, show="*")
        self.password_entry.pack(pady=5)
        ctk.CTkButton(self.main_area, text="登録", command=self.event_handlers.register_user).pack(pady=10)

    def show_main_screen(self):
        self.clear_sidebar()
        self.clear_main_area()

        ctk.CTkButton(self.sidebar, text="ダッシュボード", command=self.show_dashboard).pack(pady=10)
        ctk.CTkButton(self.sidebar, text="授業一覧", command=self.show_courses_list).pack(pady=10)
        ctk.CTkButton(self.sidebar, text="カレンダー", command=self.show_calendar).pack(pady=10)
        ctk.CTkButton(self.sidebar, text="掲示板", command=self.show_board).pack(pady=10)  # 新しく追加
        ctk.CTkButton(self.sidebar, text="ログアウト", command=self.event_handlers.logout).pack(pady=10)

        self.show_dashboard()

    def show_dashboard(self):
        self.clear_main_area()
        ctk.CTkLabel(self.main_area, text="ダッシュボード", font=("Helvetica", 24)).pack(pady=20)

        # 予定表示用のフレーム
        events_frame = ctk.CTkFrame(self.main_area)
        events_frame.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(events_frame, text="今後の予定", font=("Helvetica", 18)).pack(pady=10)

        # スクロール可能な予定リスト
        events_list = ctk.CTkScrollableFrame(events_frame, height=200)
        events_list.pack(fill="both", expand=True, padx=10, pady=5)

        # 予定を取得して表示
        events = self.db.get_user_events(self.current_user)
        today = datetime.now().date()
        upcoming_events = [e for e in events if datetime.strptime(e['date'], "%Y-%m-%d").date() >= today]
        upcoming_events.sort(key=lambda x: (x['date'], x['start_time']))

        if not upcoming_events:
            ctk.CTkLabel(events_list, text="予定はありません").pack(pady=5)
        else:
            for event in upcoming_events[:5]:  # 最大5件表示
                event_frame = ctk.CTkFrame(events_list)
                event_frame.pack(fill="x", padx=5, pady=2)
                ctk.CTkLabel(event_frame, text=f"{event['date']} {event['start_time']}-{event['end_time']}").pack(side="left", padx=5)
                ctk.CTkLabel(event_frame, text=event['name']).pack(side="left", padx=5)


    def show_courses_list(self):
        self.clear_main_area()
        ctk.CTkLabel(self.main_area, text="授業一覧", font=("Helvetica", 24)).pack(pady=20)
        courses = self.db.get_user_courses(self.current_user)
        for course in courses:
            course_frame = ctk.CTkFrame(self.main_area)
            course_frame.pack(fill="x", padx=10, pady=5)
            ctk.CTkButton(course_frame, text=course['name'], command=lambda c=course['id']: self.show_course_details(c)).pack(side="left", padx=5)
            ctk.CTkButton(course_frame, text="削除", command=lambda c=course['id']: self.event_handlers.delete_course(c)).pack(side="right", padx=5)

        ctk.CTkButton(self.main_area, text="授業を追加", command=self.event_handlers.add_course).pack(pady=10)

    def show_calendar(self):
        self.clear_main_area()
        ctk.CTkLabel(self.main_area, text="カレンダー", font=("Helvetica", 24)).pack(pady=20)
        calendar_frame = ctk.CTkFrame(self.main_area)
        calendar_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        cal = Calendar(calendar_frame, selectmode='day', date_pattern='y-mm-dd')
        cal.pack(pady=10, padx=10, fill="both", expand=True)
        
        button_frame = ctk.CTkFrame(self.main_area)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(button_frame, text="予定を追加", command=lambda: self.event_handlers.add_event(cal.get_date())).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="予定を表示", command=lambda: self.event_handlers.show_day_events(cal.get_date())).pack(side="left", padx=5)

        # イベントを持つ日にマークを付ける
        self.event_handlers.mark_event_days(cal)

    def clear_sidebar(self):
        for widget in self.sidebar.winfo_children():
            widget.destroy()

    def clear_main_area(self):
        for widget in self.main_area.winfo_children():
            widget.destroy()

    def show_course_details(self, course_id):
        self.clear_main_area()
        course = self.db.fetchone("SELECT * FROM courses WHERE id = ?", (course_id,))
        
        if course is None:
            ctk.CTkLabel(self.main_area, text="授業が見つかりません", font=("Helvetica", 24)).pack(pady=20)
            return

        ctk.CTkLabel(self.main_area, text=f"{course[2]}の詳細", font=("Helvetica", 24)).pack(pady=20)
        
        content_frame = ctk.CTkFrame(self.main_area)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(content_frame, text=f"教室: {course[3] or '未設定'}").pack(anchor="w", pady=5)
        ctk.CTkLabel(content_frame, text=f"担当教員: {course[4] or '未設定'}").pack(anchor="w", pady=5)
        ctk.CTkLabel(content_frame, text=f"授業曜日: {course[5] or '未設定'}").pack(anchor="w", pady=5)
        
        ctk.CTkLabel(content_frame, text="授業内容:").pack(anchor="w", pady=5)
        content_text = ctk.CTkTextbox(content_frame, height=200)
        content_text.pack(fill="both", expand=True, pady=5)
        content_text.insert("1.0", course[6] or "授業内容がまだ設定されていません。")
        content_text.configure(state="disabled")
        
        button_frame = ctk.CTkFrame(self.main_area)
        button_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkButton(button_frame, text="編集", command=lambda: self.event_handlers.edit_course_content(course_id)).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="戻る", command=self.show_courses_list).pack(side="right", padx=5)

    def show_add_event_window(self, date):
        add_event_window = ctk.CTkToplevel(self)
        add_event_window.title("予定を追加")
        add_event_window.geometry("400x400")
        
        ctk.CTkLabel(add_event_window, text="日付:").pack(pady=5)
        date_entry = ctk.CTkEntry(add_event_window)
        date_entry.pack(pady=5)
        date_entry.insert(0, date)
        
        ctk.CTkLabel(add_event_window, text="予定名:").pack(pady=5)
        name_entry = ctk.CTkEntry(add_event_window)
        name_entry.pack(pady=5)
        
        ctk.CTkLabel(add_event_window, text="開始時間 (HH:MM):").pack(pady=5)
        start_time_entry = ctk.CTkEntry(add_event_window)
        start_time_entry.pack(pady=5)
        
        ctk.CTkLabel(add_event_window, text="終了時間 (HH:MM):").pack(pady=5)
        end_time_entry = ctk.CTkEntry(add_event_window)
        end_time_entry.pack(pady=5)
        
        ctk.CTkButton(add_event_window, text="保存", command=lambda: self.event_handlers.save_event(
            date_entry.get(), name_entry.get(), start_time_entry.get(), end_time_entry.get(), add_event_window
        )).pack(pady=10)

    def show_day_events(self, date):
        events_window = ctk.CTkToplevel(self)
        events_window.title(f"{date}の予定")
        events_window.geometry("400x300")
        
        events = self.db.get_user_events(self.current_user)
        day_events = [e for e in events if e['date'] == date]
        
        if day_events:
            for event in day_events:
                event_frame = ctk.CTkFrame(events_window)
                event_frame.pack(fill="x", padx=10, pady=5)
                ctk.CTkLabel(event_frame, text=f"{event['name']} ({event['start_time']}-{event['end_time']})").pack(side="left", padx=5)
                ctk.CTkButton(event_frame, text="削除", command=lambda e=event['id']: self.event_handlers.delete_event(e)).pack(side="right", padx=5)
        else:
            ctk.CTkLabel(events_window, text="この日の予定はありません").pack(pady=20)
        
        ctk.CTkButton(events_window, text="予定を追加", command=lambda: self.event_handlers.add_event(date)).pack(pady=10)

    def refresh_calendar(self):
        self.show_calendar()

    def show_board(self):
        self.clear_main_area()
        ctk.CTkLabel(self.main_area, text="掲示板", font=("Helvetica", 24)).pack(pady=20)

        # スクロール可能なテキストボックスを作成
        board_frame = ctk.CTkFrame(self.main_area)
        board_frame.pack(pady=10, fill='both', expand=True)

        self.board_text = ctk.CTkTextbox(board_frame, height=300, width=500, wrap='word')
        self.board_text.pack(side='left', fill='both', expand=True)

        scrollbar = ctk.CTkScrollbar(board_frame, command=self.board_text.yview)
        scrollbar.pack(side='right', fill='y')

        self.board_text.configure(yscrollcommand=scrollbar.set, state='disabled')

        self.board_entry = ctk.CTkEntry(self.main_area, width=400)
        self.board_entry.pack(side='left', padx=10)

        ctk.CTkButton(self.main_area, text="投稿", command=self.event_handlers.post_board_message).pack(side='left')

        self.event_handlers.update_board()

    def update_board(self):
        self.event_handlers.update_board()