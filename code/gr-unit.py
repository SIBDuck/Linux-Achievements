# Copyright (C) 2026 SIBDuck
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.



import customtkinter as ctk
from PIL import Image, ImageTk
app = ctk.CTk()
"""
def set_icon():
    img = Image.open("images/tux.png")
    photo = ImageTk.PhotoImage(img)
    app.iconphoto(False, photo)
    app._icon_photo = photo

app.after(200, set_icon)
"""
app.title("Linux Achievements")
app.geometry("900x900")

def press():
    print("Button has been pressed")

but = ctk.CTkButton(app, text="hi", command=press)
but.grid(row=0, column=0, padx=20, pady=20)

app.mainloop()