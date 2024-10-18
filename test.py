import os

print(os.remove("images/.png"))

if "start.png" in os.listdir("images"):
    print(1)