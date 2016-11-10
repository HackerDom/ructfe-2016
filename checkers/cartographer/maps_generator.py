from PIL import Image, PngImagePlugin
import random
import io

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class SeafloorMapsGenerator:
    COLORS_AMOUNT = 511
    IMAGE_SIZE = 128

    def __init__(self):
        self.max = self.IMAGE_SIZE
        self.size = self.max + 1
        self.pixels = [0] * self.size * self.size
        self.offsetCoeff = 512 / self.max

    def getPixel(self, x, y):
        if (x < 0) or (x > self.max) or (y < 0) or (y > self.max):
            return -1
        return self.pixels[x + self.size * y]

    def setPixel(self, x, y, color):
        self.pixels[x + self.size * y] = color

    def getRandomColor(self):
        return random.randint(0, self.COLORS_AMOUNT)

    def getRandomOffset(self, size):
        return random.randint(-self.offsetCoeff*size, self.offsetCoeff*size)

    def getPixelsColors(self, pixelsCoordinates):
        pixelsColors = []
        for point in pixelsCoordinates:
            if self.getPixel(point.x, point.y) != -1:
                pixelsColors.append(self.getPixel(point.x, point.y))
        return pixelsColors

    def getAverage(self, numbers):
        numbersSum = 0
        for number in numbers:
            numbersSum += number
        return int(numbersSum / len(numbers))

    def getNewColor(self, average, offset):
        newColor = average + offset
        if newColor < 0:
            newColor = 0
        if newColor > self.COLORS_AMOUNT:
            newColor = self.COLORS_AMOUNT
        return newColor

    def square(self, x, y, size, offset):
        corners = self.getPixelsColors([Point(x - size, y - size), Point(x + size, y - size), Point(x + size, y + size), Point(x - size, y + size)])
        average = self.getAverage(corners)
        self.setPixel(x, y, self.getNewColor(average, offset))

    def diamond(self, x, y, size, offset):
        corners = self.getPixelsColors([Point(x, y - size), Point(x + size, y), Point(x, y + size), Point(x - size, y)])
        average = self.getAverage(corners)
        self.setPixel(x, y, self.getNewColor(average, offset))

    def divide(self, size):
        half = int(size / 2)
        if half < 1:
            return
        for y in range(half, self.max, size):
            for x in range(half, self.max, size):
                self.square(x, y, half, self.getRandomOffset(size))
        for y in range(0, self.size, half):
            for x in range((y + half) % size, self.size, size):
                self.diamond(x, y, half, self.getRandomOffset(size))

        self.divide(int(size / 2))

    def drawImage(self):
        corners = [Point(0,0), Point(0, self.max), Point(self.max, 0), Point(self.max, self.max)]
        for point in corners:
            self.setPixel(point.x, point.y, self.getRandomColor())
        self.divide(self.max)

    def generate(self):
        self.drawImage()
        image = Image.new("RGB", (self.size, self.size))
        counter = 0
        pixels = image.load()
        for i in range(image.size[0]):
            for j in range(image.size[1]):  
                if self.pixels[counter] < 256:
                    pixels[i,j] = (0, 0, self.pixels[counter])
                else:
                    pixels[i,j] = (self.pixels[counter] - 256, self.pixels[counter] - 256, 255)
                counter+=1
        return SeafloorMap(image)


class SeafloorMap:
    @classmethod
    def fromBytes(cls, byteArr):
        return SeafloorMap(Image.open(io.BytesIO(byteArr)))

    def __init__(self, image):
        self.image = image
        self.flag = ""

    def addFlag(self, flag):
        meta = PngImagePlugin.PngInfo()
        meta.add_text("additionalInfo", flag)
        self.flag = meta

    def getFlag(self):
        return self.image.info["additionalInfo"]

    def toBytes(self):
        imageByteArr = io.BytesIO()
        self.image.save(imageByteArr, format='PNG', pnginfo=self.flag)
        return imageByteArr.getvalue()

    def save(self, filename):
        self.image.save(filename, format='PNG', pnginfo=self.flag)


def main():
    generator = SeafloorMapsGenerator()
    seafloorMap = generator.generate()
    seafloorMap.addFlag("Hello!")
    byteArr = seafloorMap.toBytes()
    seafloorMap = seafloorMap.fromBytes(byteArr)
    print(seafloorMap.getFlag())
    
if __name__ == '__main__':
    main()