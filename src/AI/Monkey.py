# Class to store a monkey being used during a game

class Monkey:
    top = 0
    middle = 0
    bottom = 0

    available = ["top", "middle", "bottom"]

    def __init__(self, location, monkey_type):
        self.location = location
        self.monkey_type = monkey_type
    
    def update_rank(self, path):
        if path == "top":
            self.top += 1
            if self.top == 5:
                if "top" in self.available:
                    self.available.remove("top")
            if self.top == 1:
                if self.bottom > 0:
                    if "middle" in self.available:
                        self.available.remove("middle")
                elif self.middle > 0:
                    if "bottom" in self.available:
                        self.available.remove("bottom")
            if self.top == 2:
                if self.bottom > 2 or self.middle > 2:
                    if "top" in self.available:
                        self.available.remove("top")
            if self.top == 3:
                if self.bottom == 2:
                    if "bottom" in self.available:
                        self.available.remove("bottom")
                elif self.middle == 2:
                    if "middle" in self.available:
                        self.available.remove("middle")
        elif path == "middle":
            self.middle += 1
            if self.middle == 5:
                if "middle" in self.available:
                    self.available.remove("middle")
            if self.middle == 1:
                if self.bottom > 0:
                    if "top" in self.available:
                        self.available.remove("top")
                elif self.top > 0:
                    if "bottom" in self.available:
                        self.available.remove("bottom")
            if self.middle == 2:
                if self.bottom > 2 or self.top > 2:
                    if "middle" in self.available:
                        self.available.remove("middle")
            if self.middle == 3:
                if self.bottom == 2:
                    if "bottom" in self.available:
                        self.available.remove("bottom")
                elif self.top == 2:
                    if "top" in self.available:
                        self.available.remove("top")
        elif path == "bottom":
            self.bottom += 1
            if self.bottom == 5:
                if "bottom" in self.available:
                    self.available.remove("bottom")
            if self.bottom == 1:
                if self.middle > 0:
                    if "top" in self.available:
                        self.available.remove("top")
                elif self.top > 0:
                    if "middle" in self.available:
                        self.available.remove("middle")
            if self.bottom == 2:
                if self.middle > 2 or self.top > 2:
                    if "bottom" in self.available:
                        self.available.remove("bottom")
            if self.bottom == 3:
                if self.middle == 2:
                    if "middle" in self.available:
                        self.available.remove("middle")
                elif self.top == 2:
                    if "top" in self.available:
                        self.available.remove("top")

    def get_path_level(self, path):
        if path == "top":
            return self.top
        elif path == "middle":
            return self.middle
        else:
            return self.bottom

    def __str__(self):
        return "% s: % s - % s/% s/% s" % (self.monkey_type, self.top, self.middle, self.bottom, self.location)