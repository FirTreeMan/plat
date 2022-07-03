from PIL import Image


def pixel_rgb(imagepath, x, y):
    img = Image.open(imagepath).convert('RGB')
    r, g, b = img.getpixel((x, y))
    a = (r, g, b)
    return a


image = "input.png"

posx = 0
posy = 0
savedpixels = []
newline = False

run = True
while run:
    data = pixel_rgb(image, posx, posy)
    if posx <= 31:
        if posx < 31:
            posx += 1
        else:
            newline = True
        if data == (255, 255, 255):
            savedpixels.append(0)
        if data == (0, 0, 0):
            savedpixels.append(1)
        if data == (0, 255, 0):
            savedpixels.append(2)
        if data == (255, 0, 0):
            savedpixels.append(3)
        if data == (0, 0, 255):
            savedpixels.append(4)
        if data == (255, 0, 255):
            savedpixels.append(5)
        if data == (255, 128, 255):
            savedpixels.append(6)
        if data[0] == 255 and 128 <= data[1] < 192 and data[2] == 128:
            ident = data[1] - 128
            savedpixels.append(70 + ident)
        if data[0] == 128 and 60 <= data[1] < 128 and 60 <= data[2] < 128:
            ident = (data[1] - 60) * 10
            code = data[1] - 60
            savedpixels.append(800 + ident + code)
    if newline:
        newline = False
        posx = 0
        print(f"{savedpixels},")
        savedpixels.clear()
        if posy < 31:
            posy += 1
        else:
            run = False
