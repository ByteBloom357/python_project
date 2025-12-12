# def draw_background(canvas, key):
#     canvas.delete("all")
#     w = canvas.winfo_width() or 480
#     h = canvas.winfo_height() or 300
#     canvas.create_rectangle(0,0,w,h, fill="#888888", outline="#888888")
#     canvas.create_text(10, 10, anchor="nw", text=key.upper(), fill="white", font=("Arial", 10, "bold"))

# def draw_avatar(canvas, name):
#     canvas.delete("all")
#     w = int(canvas.cget("width"))
#     h = int(canvas.cget("height"))
#     r = min(w,h)//2 - 4
#     cx, cy = w//2, h//2
#     canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill="#ffffff", outline="")
#     if name:
#         initials = "".join([p[0] for p in name.split()][:2]).upper()
#         canvas.create_text(cx, cy, text=initials, fill="black", font=("Arial", 14, "bold"))