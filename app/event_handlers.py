import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import hashlib
import os
import shutil
from datetime import datetime
import calendar
import customtkinter as ctk
from tkinter import messagebox
import hashlib
from datetime import datetime

class EventHandlers:
    def __init__(self, app):
        self.app = app

    def login_user(self):
        email = self.app.email_entry.get()
        password = self.app.password_entry.get()
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        user = self.app.db.fetchone("SELECT * FROM users WHERE email = ? AND password = ?", (email, hashed_password))

        if user:
            self.app.current_user = email
            messagebox.showinfo("ログイン成功", "ログインに成功しました！")
            self.app.show_main_screen()
        else:
            messagebox.showerror("エラー", "メールアドレスまたはパスワードが正しくありません。")

    def register_user(self):
        name = self.app.name_entry.get()
        email = self.app.email_entry.get()
        password = self.app.password_entry.get()

        if not name or not email or not password:
            messagebox.showerror("エラー", "全てのフィールドを入力してください。")
            return

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        try:
            self.app.db.execute("INSERT INTO users (email, name, password) VALUES (?, ?, ?)",
                                (email, name, hashed_password))
            messagebox.showinfo("登録完了", "ユーザー登録が完了しました！")
            self.app.show_login_register_screen()
        except Exception as e:
            messagebox.showerror("エラー", f"ユーザー登録に失敗しました: {str(e)}")

    def logout(self):
        self.app.current_user = None
        messagebox.showinfo("ログアウト", "ログアウトしました。")
        self.app.show_login_register_screen()

    def add_course(self):
        course_name = simpledialog.askstring("授業追加", "新しい授業名を入力してください:")
        if course_name:
            self.app.db.execute("INSERT INTO courses (user_email, name) VALUES (?, ?)", (self.app.current_user, course_name))
            self.app.show_main_screen()

    def delete_course(self, course_id):
        if messagebox.askyesno("確認", "本当にこの授業を削除しますか？"):
            self.app.db.execute("DELETE FROM courses WHERE id = ?", (course_id,))
            self.app.db.execute("DELETE FROM comments WHERE course_id = ?", (course_id,))
            self.app.db.execute("DELETE FROM files WHERE course_id = ?", (course_id,))
            self.app.show_main_screen()

    def rename_course(self, course_id):
        new_name = simpledialog.askstring("授業名変更", "新しい授業名を入力してください:")
        if new_name:
            self.app.db.execute("UPDATE courses SET name = ? WHERE id = ?", (new_name, course_id))
            self.app.show_course_screen(course_id)

    def edit_course_content(self, course_id):
        edit_content_window = ctk.CTkToplevel(self.app.master)
        edit_content_window.title("授業内容編集")
        edit_content_window.geometry("400x600")

        course = self.app.db.fetchone("SELECT * FROM courses WHERE id = ?", (course_id,))

        ctk.CTkLabel(edit_content_window, text="教室:").pack(pady=5)
        classroom_entry = ctk.CTkEntry(edit_content_window, width=300)
        classroom_entry.pack(pady=5)
        classroom_entry.insert(0, course[3] or "")

        ctk.CTkLabel(edit_content_window, text="担当教員:").pack(pady=5)
        teacher_entry = ctk.CTkEntry(edit_content_window, width=300)
        teacher_entry.pack(pady=5)
        teacher_entry.insert(0, course[4] or "")

        ctk.CTkLabel(edit_content_window, text="授業曜日:").pack(pady=5)
        day_entry = ctk.CTkEntry(edit_content_window, width=300)
        day_entry.pack(pady=5)
        day_entry.insert(0, course[5] or "")

        ctk.CTkLabel(edit_content_window, text="授業内容:").pack(pady=5)
        content_text = ctk.CTkTextbox(edit_content_window, height=200, width=300)
        content_text.pack(pady=5)
        content_text.insert("1.0", course[6] or "")

        def save_content():
            new_classroom = classroom_entry.get()
            new_teacher = teacher_entry.get()
            new_day = day_entry.get()
            new_content = content_text.get("1.0", ctk.END).strip()

            try:
                self.app.db.execute("UPDATE courses SET classroom = ?, teacher = ?, day = ?, content = ? WHERE id = ?",
                                    (new_classroom, new_teacher, new_day, new_content, course_id))
                self.app.db.conn.commit()  # この行を追加
                messagebox.showinfo("保存完了", "授業内容が保存されました！")
                edit_content_window.destroy()
                self.app.show_course_details(course_id)
            except Exception as e:
                messagebox.showerror("エラー", f"データベースエラーが発生しました: {str(e)}")

        ctk.CTkButton(edit_content_window, text="保存", command=save_content).pack(pady=10)

    def upload_file(self, course_id):
        file_path = filedialog.askopenfilename()
        if file_path:
            file_name = os.path.basename(file_path)
            destination = os.path.join("uploads", f"{course_id}_{file_name}")
            os.makedirs("uploads", exist_ok=True)
            shutil.copy2(file_path, destination)
            self.app.db.execute("INSERT INTO files (course_id, filename, filepath) VALUES (?, ?, ?)",
                                (course_id, file_name, destination))
            messagebox.showinfo("アップロード完了", f"{file_name}がアップロードされました。")

    def update_course_content(self, course_id):
        course = self.app.db.fetchone("SELECT * FROM courses WHERE id = ?", (course_id,))
        self.app.course_content_text.config(state=tk.NORMAL)
        self.app.course_content_text.delete(1.0, tk.END)
        content = f"教室: {course[3]}\n\n"
        content += f"担当教員: {course[4]}\n\n"
        content += f"授業曜日: {course[5]}\n\n"
        content += f"授業内容:\n{course[6]}\n"
        self.app.course_content_text.insert(tk.END, content)
        self.app.course_content_text.config(state=tk.DISABLED)

    def update_comments(self, course_id):
        comments = self.app.db.fetchall("SELECT id, user_email, content, timestamp FROM comments WHERE course_id = ? ORDER BY timestamp DESC", (course_id,))
        self.app.comment_listbox.delete(0, tk.END)
        for comment in comments:
            self.app.comment_listbox.insert(tk.END, f"{comment[1]} - {comment[2]} ({comment[3]})")
            self.app.comment_listbox.insert(tk.END, "編集 | 削除")
            self.app.comment_listbox.insert(tk.END, "")

    def save_comment(self, course_id):
        content = self.app.comment_entry.get()
        if content:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.app.db.execute("INSERT INTO comments (course_id, user_email, content, timestamp) VALUES (?, ?, ?, ?)",
                                (course_id, self.app.current_user, content, timestamp))
            self.app.comment_entry.delete(0, tk.END)
            self.update_comments(course_id)

    def mark_event_days(self, cal):
        year, month = cal.get_displayed_month()
        first_day = f"{year:04d}-{month:02d}-01"
        last_day = f"{year:04d}-{month:02d}-{calendar.monthrange(year, month)[1]:02d}"

        events = self.app.db.fetchall("SELECT date FROM events WHERE user_email = ? AND date BETWEEN ? AND ? GROUP BY date", 
                                    (self.app.current_user, first_day, last_day))

        for (date,) in events:
            cal.calevent_create(date=date, text="予定あり", tags=["event"])

        cal.tag_config("event", background="light blue")

    def show_day_events(self, date):
        event_window = tk.Toplevel(self.app.root)
        event_window.title(f"{date}の予定")

        events = self.app.db.fetchall("SELECT id, name, start_time, end_time FROM events WHERE user_email = ? AND date = ?", 
                                      (self.app.current_user, date))

        if events:
            for event in events:
                event_frame = tk.Frame(event_window)
                event_frame.pack(fill=tk.X, padx=5, pady=5)
                tk.Label(event_frame, text=f"{event[1]} ({event[2]}-{event[3]})").pack(side=tk.LEFT)
                tk.Button(event_frame, text="削除", command=lambda e=event[0]: self.delete_event(e)).pack(side=tk.RIGHT)
        else:
            tk.Label(event_window, text="この日の予定はありません").pack(pady=5)

        tk.Button(event_window, text="予定を追加", command=lambda: self.add_event(date)).pack(pady=10)

    def add_event(self, date=None):
        add_event_window = ctk.CTkToplevel(self.app.master)
        add_event_window.title("予定を追加")
        add_event_window.geometry("400x400")

        ctk.CTkLabel(add_event_window, text="日付:").pack(pady=5)
        date_entry = ctk.CTkEntry(add_event_window)
        date_entry.pack(pady=5)
        if date:
            # 日付フォーマットを確認し、必要に応じて変換
            try:
                formatted_date = datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d")
                date_entry.insert(0, formatted_date)
            except ValueError:
                messagebox.showerror("エラー", "無効な日付形式です。YYYY-MM-DD形式で入力してください。")
                return

        ctk.CTkLabel(add_event_window, text="予定名:").pack(pady=5)
        name_entry = ctk.CTkEntry(add_event_window)
        name_entry.pack(pady=5)

        ctk.CTkLabel(add_event_window, text="開始時間 (HH:MM):").pack(pady=5)
        start_time_entry = ctk.CTkEntry(add_event_window)
        start_time_entry.pack(pady=5)

        ctk.CTkLabel(add_event_window, text="終了時間 (HH:MM):").pack(pady=5)
        end_time_entry = ctk.CTkEntry(add_event_window)
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
                self.app.db.execute("INSERT INTO events (user_email, date, name, start_time, end_time) VALUES (?, ?, ?, ?, ?)",
                                    (self.app.current_user, event_date, event_name, start_time, end_time))
                messagebox.showinfo("追加完了", "予定が追加されました。")
                add_event_window.destroy()
                self.app.show_calendar()  # カレンダーを更新
            except Exception as e:
                messagebox.showerror("エラー", f"予定の追加に失敗しました: {str(e)}")

        ctk.CTkButton(add_event_window, text="保存", command=save_event).pack(pady=10)

    def edit_event(self, date):
        edit_event_window = tk.Toplevel(self.app.root)
        edit_event_window.title(f"{date}の予定編集")

        events = self.app.db.fetchall("SELECT id, name, start_time, end_time FROM events WHERE user_email = ? AND date = ?", 
                                      (self.app.current_user, date))

        if not events:
            tk.Label(edit_event_window, text="この日の予定はありません").pack(pady=10)
            return

        for event in events:
            event_frame = tk.Frame(edit_event_window)
            event_frame.pack(fill=tk.X, padx=5, pady=5)
            
            tk.Label(event_frame, text=f"{event[1]} ({event[2]}-{event[3]})").pack(side=tk.LEFT)
            tk.Button(event_frame, text="編集", command=lambda e=event: self.edit_single_event(e)).pack(side=tk.RIGHT)
            tk.Button(event_frame, text="削除", command=lambda e=event[0]: self.delete_event(e)).pack(side=tk.RIGHT)

    def edit_single_event(self, event):
        edit_window = tk.Toplevel(self.app.root)
        edit_window.title("予定を編集")

        tk.Label(edit_window, text="予定名:").pack(pady=5)
        name_entry = tk.Entry(edit_window)
        name_entry.insert(0, event[1])
        name_entry.pack(pady=5)

        tk.Label(edit_window, text="開始時間 (HH:MM):").pack(pady=5)
        start_time_entry = tk.Entry(edit_window)
        start_time_entry.insert(0, event[2])
        start_time_entry.pack(pady=5)

        tk.Label(edit_window, text="終了時間 (HH:MM):").pack(pady=5)
        end_time_entry = tk.Entry(edit_window)
        end_time_entry.insert(0, event[3])
        end_time_entry.pack(pady=5)

        def save_edited_event():
            new_name = name_entry.get()
            new_start_time = start_time_entry.get()
            new_end_time = end_time_entry.get()

            try:
                self.app.db.execute("UPDATE events SET name = ?, start_time = ?, end_time = ? WHERE id = ?",
                                    (new_name, new_start_time, new_end_time, event[0]))
                messagebox.showinfo("編集完了", "予定が更新されました。")
                edit_window.destroy()
                self.app.refresh_calendar()
            except Exception as e:
                messagebox.showerror("エラー", f"予定の更新に失敗しました: {str(e)}")

        tk.Button(edit_window, text="保存", command=save_edited_event).pack(pady=10)

    def delete_event(self, event_id):
        if messagebox.askyesno("確認", "本当にこの予定を削除しますか？"):
            try:
                self.app.db.execute("DELETE FROM events WHERE id = ?", (event_id,))
                messagebox.showinfo("削除完了", "予定が削除されました。")
                self.app.refresh_calendar()
            except Exception as e:
                messagebox.showerror("エラー", f"予定の削除に失敗しました: {str(e)}")

    def refresh_calendar(self):
        for child in self.app.root.winfo_children():
            if isinstance(child, ttk.Notebook):
                for tab in child.winfo_children():
                    if child.tab(tab)['text'] == 'カレンダー':
                        self.app.show_calendar(tab)
                        break
                break

    def display_upcoming_events(self, parent_frame):
        # 現在の日付から2週間分の予定を取得
        today = datetime.now().date()
        two_weeks_later = today + timedelta(days=14)
        
        events = self.app.db.fetchall("""
            SELECT date, name, start_time, end_time 
            FROM events 
            WHERE user_email = ? AND date BETWEEN ? AND ? 
            ORDER BY date, start_time
        """, (self.app.current_user, today, two_weeks_later))

        if not events:
            ctk.CTkLabel(parent_frame, text="予定はありません").pack(pady=5)
        else:
            for event in events:
                event_date = datetime.strptime(event[0], "%Y-%m-%d").date()
                event_frame = ctk.CTkFrame(parent_frame)
                event_frame.pack(fill="x", padx=5, pady=2)
                
                date_str = event_date.strftime("%m/%d")
                time_str = f"{event[2]} - {event[3]}"
                
                ctk.CTkLabel(event_frame, text=f"{date_str} {time_str}").pack(side="left", padx=5)
                ctk.CTkLabel(event_frame, text=event[1]).pack(side="left", padx=5)        