import json

from schema import loader

config_path = "../instance/flash_complete_config.json"
with open(config_path) as file:
    # Load the JSON data from the file
    data = json.load(file)

print(loader.LoaderConfig(**data))
