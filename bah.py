x1 = 0
x2 = 40
ox1 = 40
ox2 = 60

y1 = 0
y2 = 40
oy1 = 20
oy2 = 60



if ((x1 <= ox1 < x2) or (x1 < ox2 <= x2) or (ox1 < x1 < ox2)) and ((y1 <= oy1 < y2) or (y1 < oy2 <= y2) or (oy1 < y1 < oy2)) :
    print("collision")

 # and (
 #        (y1 <= oy1 < y2) or (y1 < oy2 <= y2) or (oy1 < y1 < oy2)):