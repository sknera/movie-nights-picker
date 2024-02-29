import tkinter as tk
from PIL import Image, ImageTk
import random
import gspread
import pandas as pd
import math
# (Same code for importing data and setting up the DataFrame)

class SpinningWheelApp:
    def __init__(self, root):
        self.root = root
        root.geometry("400x600")
        self.canvas = tk.Canvas(root, width=400, height=400)
        self.root.title("Koło fortuny")

        self.spin_button = tk.Button(root, text="Zakręć kołem", command=self.spin_wheel)
        self.spin_button.pack(pady=20)

        self.result_label = tk.Label(root, text="Gatunek: ")
        self.result_label.pack()

        self.column_label = tk.Label(root, text="Wybierał: ")
        self.column_label.pack()

        self.original_image = Image.open("wheel.png")  # Load your wheel image
        self.tk_image = ImageTk.PhotoImage(self.original_image)
        self.wheel_canvas_item = self.canvas.create_image(200, 200, image=self.tk_image)

    def get_random(self, df):
        real_headers=[x for x in df.columns if isinstance(x,str)]
        occurences = list()
        for  person in real_headers:
            for topic in df[person]:
                if pd.isna(person) or pd.isna(topic):
                    continue
                else:
                    occurences.append((person,topic))
        return random.choice(occurences)

    def spin_wheel(self):
        angle = 0
        for _ in range(36):  # Number of frames for the spinning animation
            rotated_image = self.original_image.rotate(angle)  # Rotate the image
            self.tk_image = ImageTk.PhotoImage(rotated_image)
            self.canvas.itemconfig(self.wheel_canvas_item, image=self.tk_image)
            self.root.update()  # Update the window
            self.root.after(50)  # Delay for smooth animation
            angle += 10  # Rotate by 10 degrees in each frame

        random_value, random_column = "nan", "nan"
        while str(random_value)=="nan" or str(random_column)=="nan":
            random_value, random_column = self.get_random(df)
            
        self.result_label.config(text=f"Wygrało: {random_value}")
        self.column_label.config(text=f"Wybierał: {random_column}")

if __name__ == "__main__":
    excel_file_path = 'spread.xlsx'
    df = pd.read_excel(excel_file_path, header=None)  # Read without header
    headers = df.iloc[0]
    df = df.iloc[1:]  # Skip the first row as it is now headers
    df.columns = headers  # Set headers
    root = tk.Tk()
    app = SpinningWheelApp(root)
    app.canvas.pack()
    root.mainloop()
