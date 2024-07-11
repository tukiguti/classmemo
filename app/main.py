import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog, ttk
import os
import json
import hashlib
import sqlite3
from datetime import datetime
import calendar
from tkcalendar import Calendar
import shutil

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("授業管理システム")
        self.root.geometry("1024x768")
        self.current_user = None
        self.init_database()
        self.show_login_register_screen()

    def init_database(self):
        self.conn = sqlite3.connect('class_management.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users
                            (email TEXT PRIMARY KEY, name TEXT, password TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS courses
                            (id INTEGER PRIMARY KEY, user_email TEXT, name TEXT, classroom TEXT, teacher TEXT, day TEXT, content TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS comments
                            (id INTEGER PRIMARY KEY, course_id INTEGER, user_email TEXT, content TEXT, timestamp TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS files
                            (id INTEGER PRIMARY KEY, course_id INTEGER, filename TEXT, filepath TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS events
                            (id INTEGER PRIMARY KEY, user_email TEXT, date TEXT, name TEXT, start_time TEXT, end_time TEXT)''')
        self.conn.commit()

    # Show メソッド群
    def show_login_register_screen(self):
        self.clear_screen()
        login_btn = tk.Button(self.root, text="ログイン", command=self.show_login_window)
        login_btn.pack(pady=10)
        register_btn = tk.Button(self.root, text="ユーザー登録", command=self.show_register_window)
        register_btn.pack(pady=10)

    def show_login_window(self):
        self.clear_screen()
        tk.Label(self.root, text="メールアドレス:").pack(pady=5)
        self.email_entry = tk.Entry(self.root)
        self.email_entry.pack(pady=5)
        tk.Label(self.root, text="パスワード:").pack(pady=5)
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack(pady=5)
        tk.Button(self.root, text="ログイン", command=self.login_user).pack(pady=10)
        tk.Button(self.root, text="戻る", command=self.show_login_register_screen).pack(pady=10)

    def show_register_window(self):
        self.clear_screen()
        tk.Label(self.root, text="名前:").pack(pady=5)
        self.name_entry = tk.Entry(self.root)
        self.name_entry.pack(pady=5)
        tk.Label(self.root, text="メールアドレス:").pack(pady=5)
        self.email_entry = tk.Entry(self.root)
        self.email_entry.pack(pady=5)
        tk.Label(self.root, text="パスワード:").pack(pady=5)
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack(pady=5)
        tk.Button(self.root, text="登録", command=self.register_user).pack(pady=10)
        tk.Button(self.root, text="戻る", command=self.show_login_register_screen).pack(pady=10)

    def show_main_screen(self):
        self.clear_screen()
        self.cursor.execute("SELECT name FROM users WHERE email = ?", (self.current_user,))
        user_name = self.cursor.fetchone()[0]
        tk.Label(self.root, text=f"{user_name}さんのダッシュボード").pack(pady=10)

        notebook = ttk.Notebook(self.root)
        notebook.pack(pady=10, expand=True, fill=tk.BOTH)

        courses_frame = ttk.Frame(notebook)
        notebook.add(courses_frame, text="授業一覧")
        self.show_courses_list(courses_frame)

        calendar_frame = ttk.Frame(notebook)
        notebook.add(calendar_frame, text="カレンダー")
        self.show_calendar(calendar_frame)

        tk.Button(self.root, text="ログアウト", command=self.logout).pack(pady=10)
    
    def show_courses_list(self, parent_frame):
        self.cursor.execute("SELECT id, name FROM courses WHERE user_email = ?", (self.current_user,))
        courses = self.cursor.fetchall()

        for course_id, course_name in courses:
            frame = tk.Frame(parent_frame)
            frame.pack(pady=5)
            tk.Button(frame, text=course_name, command=lambda c=course_id: self.show_course_screen(c)).pack(side=tk.LEFT)
            tk.Button(frame, text="削除", command=lambda c=course_id: self.delete_course(c)).pack(side=tk.LEFT)

        tk.Button(parent_frame, text="授業を追加", command=self.add_course).pack(pady=10)

    def show_course_screen(self, course_id):
        self.clear_screen()
        self.cursor.execute("SELECT * FROM courses WHERE id = ?", (course_id,))
        course = self.cursor.fetchone()

        tk.Label(self.root, text=f"{course[2]}の詳細").pack(pady=10)
        tk.Button(self.root, text="授業名変更", command=lambda: self.rename_course(course_id)).pack(pady=10)
        tk.Button(self.root, text="授業内容編集", command=lambda: self.edit_course_content(course_id)).pack(pady=10)
        tk.Button(self.root, text="ファイルアップロード", command=lambda: self.upload_file(course_id)).pack(pady=10)
        tk.Button(self.root, text="戻る", command=self.show_main_screen).pack(pady=10)

        self.course_content_text = tk.Text(self.root, height=10, width=50)
        self.update_course_content(course_id)
        self.course_content_text.config(state=tk.DISABLED)
        self.course_content_text.pack(pady=10)

        tk.Label(self.root, text="コメント").pack(pady=10)
        self.comment_listbox = tk.Listbox(self.root, height=10)
        self.comment_listbox.pack(pady=5, fill=tk.BOTH, expand=True)

        self.update_comments(course_id)

        tk.Label(self.root, text="コメントを入力:").pack(pady=5)
        self.comment_entry = tk.Entry(self.root)
        self.comment_entry.pack(pady=5)

        tk.Button(self.root, text="投稿", command=lambda: self.save_comment(course_id)).pack(pady=5)
        tk.Button(self.root, text="コメント更新", command=lambda: self.update_comments(course_id)).pack(pady=5)

    def show_calendar(self, parent_frame):
        current_date = datetime.now()
        year = current_date.year
        month = current_date.month

        cal = Calendar(parent_frame, selectmode='day', year=year, month=month, locale='ja_JP')
        cal.pack(pady=20, expand=True, fill=tk.BOTH)

        self.mark_event_days(cal)

        button_frame = tk.Frame(parent_frame)
        button_frame.pack(pady=10, fill=tk.X)

        def show_selected_date():
            selected_date = cal.get_date()
            self.show_day_events(selected_date)

        tk.Button(button_frame, text="選択した日付の予定を表示", command=show_selected_date).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="予定を追加", command=lambda: self.add_event(cal.get_date())).pack(side=tk.LEFT, padx=5)

        # カレンダーの更新用関数
        def refresh_calendar():
            self.mark_event_days(cal)
            parent_frame.after(60000, refresh_calendar)  # 1分ごとに更新

        refresh_calendar()

    def show_day_events(self, date):
        event_window = tk.Toplevel(self.root)
        event_window.title(f"{date}の予定")

        self.cursor.execute("SELECT id, name, start_time, end_time FROM events WHERE user_email = ? AND date = ?", 
                            (self.current_user, date))
        events = self.cursor.fetchall()

        if events:
            for event in events:
                event_frame = tk.Frame(event_window)
                event_frame.pack(fill=tk.X, padx=5, pady=5)
                tk.Label(event_frame, text=f"{event[1]} ({event[2]}-{event[3]})").pack(side=tk.LEFT)
                tk.Button(event_frame, text="削除", command=lambda e=event[0]: self.delete_event(e)).pack(side=tk.RIGHT)
        else:
            tk.Label(event_window, text="この日の予定はありません").pack(pady=5)

        tk.Button(event_window, text="予定を追加", command=lambda: self.add_event(date)).pack(pady=10)

    # Edit メソッド群
    def edit_course_content(self, course_id):
        edit_content_window = tk.Toplevel(self.root)
        edit_content_window.title("授業内容編集")
        edit_content_window.geometry("400x500")

        self.cursor.execute("SELECT * FROM courses WHERE id = ?", (course_id,))
        course = self.cursor.fetchone()

        tk.Label(edit_content_window, text="教室:").pack(pady=5)
        classroom_entry = tk.Entry(edit_content_window, width=50)
        classroom_entry.pack(pady=5)
        classroom_entry.insert(0, course[3] or "")

        tk.Label(edit_content_window, text="担当教員:").pack(pady=5)
        teacher_entry = tk.Entry(edit_content_window, width=50)
        teacher_entry.pack(pady=5)
        teacher_entry.insert(0, course[4] or "")

        tk.Label(edit_content_window, text="授業曜日:").pack(pady=5)
        day_entry = tk.Entry(edit_content_window, width=50)
        day_entry.pack(pady=5)
        day_entry.insert(0, course[5] or "")

        tk.Label(edit_content_window, text="授業内容:").pack(pady=5)
        content_text = tk.Text(edit_content_window, height=10, width=50)
        content_text.pack(pady=5)
        content_text.insert(tk.END, course[6] or "")

        def save_content():
            new_classroom = classroom_entry.get()
            new_teacher = teacher_entry.get()
            new_day = day_entry.get()
            new_content = content_text.get("1.0", tk.END).strip()

            try:
                self.cursor.execute("UPDATE courses SET classroom = ?, teacher = ?, day = ?, content = ? WHERE id = ?",
                                    (new_classroom, new_teacher, new_day, new_content, course_id))
                self.conn.commit()
                messagebox.showinfo("保存完了", "授業内容が保存されました！")
                edit_content_window.destroy()
                self.show_course_screen(course_id)
            except sqlite3.Error as e:
                messagebox.showerror("エラー", f"データベースエラーが発生しました: {e}")

        tk.Button(edit_content_window, text="保存", command=save_content).pack(pady=10)

    def edit_comment(self, comment_id):
        self.cursor.execute("SELECT content FROM comments WHERE id = ?", (comment_id,))
        old_content = self.cursor.fetchone()[0]
        new_content = simpledialog.askstring("コメント編集", "新しいコメントを入力してください:", initialvalue=old_content)
        if new_content:
            self.cursor.execute("UPDATE comments SET content = ? WHERE id = ?", (new_content, comment_id))
            self.conn.commit()
            self.update_comments(self.cursor.execute("SELECT course_id FROM comments WHERE id = ?", (comment_id,)).fetchone()[0])

    # Add メソッド群
    def add_course(self):
        course_name = simpledialog.askstring("授業追加", "新しい授業名を入力してください:")
        if course_name:
            self.cursor.execute("INSERT INTO courses (user_email, name) VALUES (?, ?)", (self.current_user, course_name))
            self.conn.commit()
            self.show_main_screen()

    def add_event(self, date=None):
        add_event_window = tk.Toplevel(self.root)
        add_event_window.title("予定を追加")

        tk.Label(add_event_window, text="日付:").pack(pady=5)
        date_entry = tk.Entry(add_event_window)
        date_entry.pack(pady=5)
        if date:
            date_entry.insert(0, date)

        tk.Label(add_event_window, text="予定名:").pack(pady=5)
        name_entry = tk.Entry(add_event_window)
        name_entry.pack(pady=5)

        tk.Label(add_event_window, text="開始時間 (HH:MM):").pack(pady=5)
        start_time_entry = tk.Entry(add_event_window)
        start_time_entry.pack(pady=5)

        tk.Label(add_event_window, text="終了時間 (HH:MM):").pack(pady=5)
        end_time_entry = tk.Entry(add_event_window)
        end_time_entry.pack(pady=5)

        def save_event():
            event_date = date_entry.get()
            event_name = name_entry.get()
            start_time = start_time_entry.get()
            end_time = end_time_entry.get()

            if not event_date or not event_name or not start_time or not end_time:
                messagebox.showerror("エラー", "全てのフィールドを入力してください。")
                return

            try:
                self.cursor.execute("INSERT INTO events (user_email, date, name, start_time, end_time) VALUES (?, ?, ?, ?, ?)",
                                    (self.current_user, event_date, event_name, start_time, end_time))
                self.conn.commit()
                messagebox.showinfo("追加完了", "予定が追加されました。")
                add_event_window.destroy()
                if date:
                    self.show_day_events(date)
                # カレンダータブを探して更新
                for child in self.root.winfo_children():
                    if isinstance(child, ttk.Notebook):
                        for tab in child.winfo_children():
                            if child.tab(tab)['text'] == 'カレンダー':
                                self.show_calendar(tab)
                                break
                        break
            except sqlite3.Error as e:
                messagebox.showerror("エラー", f"データベースエラーが発生しました: {e}")

        tk.Button(add_event_window, text="保存", command=save_event).pack(pady=10)


    # Delete メソッド群
    def delete_course(self, course_id):
        if messagebox.askyesno("確認", "本当にこの授業を削除しますか？"):
            self.cursor.execute("DELETE FROM courses WHERE id = ?", (course_id,))
            self.cursor.execute("DELETE FROM comments WHERE course_id = ?", (course_id,))
            self.cursor.execute("DELETE FROM files WHERE course_id = ?", (course_id,))
            self.conn.commit()
            self.show_main_screen()

    def delete_comment(self, comment_id):
        if messagebox.askyesno("確認", "本当にこのコメントを削除しますか？"):
            course_id = self.cursor.execute("SELECT course_id FROM comments WHERE id = ?", (comment_id,)).fetchone()[0]
            self.cursor.execute("DELETE FROM comments WHERE id = ?", (comment_id,))
            self.conn.commit()
            self.update_comments(course_id)

    def delete_event(self, event_id):
        if messagebox.askyesno("確認", "本当にこの予定を削除しますか？"):
            try:
                self.cursor.execute("DELETE FROM events WHERE id = ?", (event_id,))
                self.conn.commit()
                messagebox.showinfo("削除完了", "予定が削除されました。")
                # 現在の日付イベント画面を更新
                self.show_day_events(self.cursor.execute("SELECT date FROM events WHERE id = ?", (event_id,)).fetchone()[0])
            except sqlite3.Error as e:
                messagebox.showerror("エラー", f"データベースエラーが発生しました: {e}")

    # Update メソッド群
    def update_course_content(self, course_id):
        self.cursor.execute("SELECT * FROM courses WHERE id = ?", (course_id,))
        course = self.cursor.fetchone()
        self.course_content_text.config(state=tk.NORMAL)
        self.course_content_text.delete(1.0, tk.END)
        content = f"教室: {course[3]}\n\n"
        content += f"担当教員: {course[4]}\n\n"
        content += f"授業曜日: {course[5]}\n\n"
        content += f"授業内容:\n{course[6]}\n"
        self.course_content_text.insert(tk.END, content)
        self.course_content_text.config(state=tk.DISABLED)

    def update_comments(self, course_id):
        self.cursor.execute("SELECT id, user_email, content, timestamp FROM comments WHERE course_id = ? ORDER BY timestamp DESC", (course_id,))
        comments = self.cursor.fetchall()

        self.comment_listbox.delete(0, tk.END)
        for comment in comments:
            self.comment_listbox.insert(tk.END, f"{comment[1]} - {comment[2]} ({comment[3]})")
            self.comment_listbox.insert(tk.END, "編集 | 削除")
            self.comment_listbox.insert(tk.END, "")

        self.comment_listbox.bind('<Double-Button-1>', lambda event: self.comment_action(event, course_id))

    # その他のメソッド
    def register_user(self):
        name = self.name_entry.get()
        email = self.email_entry.get()
        password = self.password_entry.get()

        if not name or not email or not password:
            messagebox.showerror("エラー", "全てのフィールドを入力してください。")
            return

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        try:
            self.cursor.execute("INSERT INTO users (email, name, password) VALUES (?, ?, ?)",
                                (email, name, hashed_password))
            self.conn.commit()
            messagebox.showinfo("登録完了", "ユーザー登録が完了しました！")
            self.show_login_register_screen()
        except sqlite3.IntegrityError:
            messagebox.showerror("エラー", "このメールアドレスは既に登録されています。")

    def login_user(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        self.cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, hashed_password))
        user = self.cursor.fetchone()

        if user:
            self.current_user = email
            messagebox.showinfo("ログイン成功", "ログインに成功しました！")
            self.show_main_screen()
        else:
            messagebox.showerror("エラー", "メールアドレスまたはパスワードが正しくありません。")

    def logout(self):
        self.current_user = None
        messagebox.showinfo("ログアウト", "ログアウトしました。")
        self.show_login_register_screen()

    def rename_course(self, course_id):
        new_name = simpledialog.askstring("授業名変更", "新しい授業名を入力してください:")
        if new_name:
            self.cursor.execute("UPDATE courses SET name = ? WHERE id = ?", (new_name, course_id))
            self.conn.commit()
            self.show_main_screen()

    def comment_action(self, event, course_id):
        selection = self.comment_listbox.curselection()
        if selection:
            index = selection[0]
            if index % 3 == 1:  # "編集 | 削除" の行がクリックされた場合
                comment_id = self.cursor.execute("SELECT id FROM comments WHERE course_id = ? ORDER BY timestamp DESC LIMIT 1 OFFSET ?", (course_id, index // 3)).fetchone()[0]
                action = simpledialog.askstring("アクション", "編集または削除を入力してください:")
                if action == "編集":
                    self.edit_comment(comment_id)
                elif action == "削除":
                    self.delete_comment(comment_id)

    def save_comment(self, course_id):
        content = self.comment_entry.get()
        if content:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute("INSERT INTO comments (course_id, user_email, content, timestamp) VALUES (?, ?, ?, ?)",
                                (course_id, self.current_user, content, timestamp))
            self.conn.commit()
            self.comment_entry.delete(0, tk.END)
            self.update_comments(course_id)

    def upload_file(self, course_id):
        file_path = filedialog.askopenfilename()
        if file_path:
            file_name = os.path.basename(file_path)
            destination = os.path.join("uploads", f"{course_id}_{file_name}")
            os.makedirs("uploads", exist_ok=True)
            shutil.copy2(file_path, destination)
            self.cursor.execute("INSERT INTO files (course_id, filename, filepath) VALUES (?, ?, ?)",
                                (course_id, file_name, destination))
            self.conn.commit()
            messagebox.showinfo("アップロード完了", f"{file_name}がアップロードされました。")

    def mark_event_days(self, cal):
        first_day = f"{cal.get_displayed_month()[0]:04d}-{cal.get_displayed_month()[1]:02d}-01"
        last_day = f"{cal.get_displayed_month()[0]:04d}-{cal.get_displayed_month()[1]:02d}-{calendar.monthrange(cal.get_displayed_month()[0], cal.get_displayed_month()[1])[1]:02d}"

        self.cursor.execute("SELECT date, COUNT(*) FROM events WHERE user_email = ? AND date BETWEEN ? AND ? GROUP BY date", 
                            (self.current_user, first_day, last_day))
        events = self.cursor.fetchall()

        for date, count in events:
            cal.calevent_create(date=date, text=f"{count}件の予定", tags=["event"])

        cal.tag_config("event", background="light blue")

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()   