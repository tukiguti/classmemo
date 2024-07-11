import customtkinter as ctk
from ui_components import App

if __name__ == "__main__":
    try:
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        root = ctk.CTk()
        root.geometry("800x600")
        app = App(root)
        print("Entering main loop")
        root.mainloop()
    except Exception as e:
        print(f"An error occurred: {e}")
        print(traceback.format_exc())