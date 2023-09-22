import ujson


class ConfigManager:
    def __init__(self, filename):
        self.filename = filename
        self.load_cache()
        self.confirm_config_init()

    def confirm_config_init(self):
        for key, val in ConfigManager.DEFAULT_CONFIG.items():
            if key not in self.cache:
                self.cache[key] = val
        self.save_cache()

    def load_cache(self):
        try:
            f = open(self.filename)
            self.cache = ujson.load(f)
        except OSError:
            f = open(self.filename, "w+")
            self.cache = {}
        f.close()

    def read(self, key):
        return self.cache[key]

    def save_cache(self):
        with open(self.filename, "w") as f:
            ujson.dump(self.cache, f)

    def write(self, key, value):
        self.cache[key] = value
        self.save_cache()

    DEFAULT_CONFIG = {
        "weights": {
            "LB": {
                "plates": {
                    "55": {"using": False, "value": 5500},
                    "45": {"using": True, "value": 4500},
                    "35": {"using": False, "value": 3500},
                    "25": {"using": True, "value": 2500},
                    "10": {"using": True, "value": 1000},
                    "5": {"using": True, "value": 500},
                    "2.5": {"using": True, "value": 250},
                    "1.25": {"using": False, "value": 125},
                },
                "bars": {
                    "45": {"using": True, "value": 45},
                    "35": {"using": False, "value": 35},
                },
                "bar": 45,
                "collars": {"0": {"using": True, "value": 0}},
                "collar": 0,
            },
            "KG": {
                "plates": {
                    "25": {"using": True, "value": 2500},
                    "20": {"using": True, "value": 2000},
                    "15": {"using": True, "value": 1500},
                    "10": {"using": True, "value": 1000},
                    "5": {"using": True, "value": 500},
                    "2.5": {"using": True, "value": 250},
                    "1.25": {"using": True, "value": 125},
                },
                "bars": {
                    "20": {"using": True, "value": 20},
                    "15": {"using": False, "value": 15},
                },
                "bar": 20,
                "collars": {
                    "0": {"using": True, "value": 0},
                    "1.25": {"using": False, "value": 125},
                    "2.5": {"using": False, "value": 250},
                },
                "collar": 0,
            },
        },
        "prompt": {"unit_state": 0},
    }
