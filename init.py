import os

base_path = os.path.dirname(__file__)
modules_path = os.path.join(base_path, "modules")

for folder in os.listdir(modules_path):
    mod_path = os.path.join(modules_path, folder, "module.py")
    print(f"{folder} => {'✅' if os.path.exists(mod_path) else '❌'}")
