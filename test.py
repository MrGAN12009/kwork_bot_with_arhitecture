import os

print(os.listdir("images"))

if "start.png" in os.listdir("images"):
    print(1)