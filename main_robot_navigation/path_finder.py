from shapely.geometry import LineString, Polygon, Point
import matplotlib.pyplot as plt

# make a class for a point
# index 0: point
# index 1: path to that point
# index 2: True/False for the point to be used in calculations

# range = how close can the center of the robot get to the borders while navigating(ideal 60% of the diameter)
class Path_Finder:
    def __init__ (self, contours = [], points = [], h_w = None, range = 165):
        self.contours = contours
        self.hw = h_w
        self.range = range
        self.points = self.populate(points)
    
    def update(self, contours = [], points = [], h_w = None, range = 165):
        self.contours = contours
        self.hw = h_w
        self.range = range
        self.points = self.populate(points)

    def populate (self, points):
        self.polygons = []

        for contour in self.contours:
            self.polygons.append(Polygon(contour))
            
        self.contours = self.reshape(self.contours)
        for point in points:
            self.contours.append([point])

    def reshape (self, contours):
        new_contours = []
        for contour in contours:
            for point in contour:
                if self.hw != None:
                    if point[0] <= self.range or point[1] <= self.range:
                        continue
                    if point[0] >= self.hw[1]-self.range or point[1] >= self.hw[0]-self.range:
                        continue
                new_contours.append([point])
        return new_contours

    def is_line_on_polygon_border(self, line):
        line_string = LineString(line)
        for polygon in self.polygons:
            if polygon.touches(line_string):
                return True
        return False

    def is_line_intersecting_any_polygon(self, line):
        line_string = LineString(line)
        for polygon in self.polygons:
            if polygon.intersects(line_string):
                if self.is_line_on_polygon_border(line):
                    continue
                else:
                    return True
        return False
    
    def is_line_crossing_any_polygon(self, line):
        line_string = LineString(line)
        for polygon in self.polygons:
            if line_string.crosses(polygon):
                return True
        return False
    
    def is_line_within_any_polygon(self, line):
        line_string = LineString(line)
        for polygon in self.polygons:
            if line_string.within(polygon):
                return True
        return False
    
    def is_point_inside_any_polygon(self, point):
        point = Point(point)
        for polygon in self.polygons:
            if point.within(polygon):
                return True
        return False

    def find_path (self, start, end):
        if self.is_point_inside_any_polygon(start) or self.is_point_inside_any_polygon(end):
            raise("Error start/end is inside contour")
            # print("Error start/end is inside contour")
        used_nodes = []
        start = [start, [[start]]]
        used_nodes.append(start)
        end = [end, []]

        for point in self.contours:
            point.append([])
            point.append(False)

        while used_nodes:
            for node in used_nodes:
                self.make_pathes(node, end)
            
            used_nodes = []
            z = 0
            range = len(self.contours)
            while z < range:
                if self.contours[z][2]:
                    used_nodes.append(self.contours.pop(z))
                    range -= 1
                    z -= 1
                z += 1
        self.paths = end[1]

        return end[1]

    def make_pathes (self, start, end):
        if not self.check_path(start, end):
            for contour in self.contours:
                if self.check_path(start, contour):
                    contour[2] = True
        return

    def check_path (self, start, end):
        line = [start[0], end[0]]

        if not (self.is_line_crossing_any_polygon(line) or 
                self.is_line_intersecting_any_polygon(line) or 
                self.is_line_within_any_polygon(line)):
            for path in start[1]:
                new_path = path.copy()
                new_path.append(end[0])
                end[1].append(new_path)
            return True
        return False
    
    def find_shortest_path(self):
        lines = []
        for path in self.paths:
            lines.append([LineString(path).length, path])
        lines.sort(key=lambda x: x[0])
        print(lines)
        return lines[0][1]
    
    def draw_graph (self):
        fig, ax = plt.subplots()

        for polygon in self.polygons:
            x, y = polygon.exterior.xy
            ax.fill(x, y, alpha=0.5)

        for path in self.paths:
            x, y = LineString(path).xy
            ax.plot(x, y, linewidth=2, label='Line')
        
        plt.show()

    def draw_line (self, line):
        fig, ax = plt.subplots()

        for polygon in self.polygons:
            x, y = polygon.exterior.xy
            ax.fill(x, y, alpha=0.5)

        x, y = line.xy
        ax.plot(x, y, linewidth=2, label='Line')
        
        plt.show()

        return

