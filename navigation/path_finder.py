from shapely.geometry import LineString, Polygon, Point, box, MultiPoint, MultiPolygon, GeometryCollection
from shapely.ops import unary_union
import numpy as np
import math
import networkx as nx
# import cv2 as cv
# import matplotlib.pyplot as plt

# make a class for a point
# index 0: point
# index 1: path to that point
# index 2: True/False for the point to be used in calculations

# range = how close can the center of the robot get to the borders while navigating(ideal 60% of the diameter)
class Path_Finder:
    def __init__ (self, offset, contours = [], default_contours = [], points = [], h_w = None, range = 200, cluster_objects = False):
        self.contours = contours
        self.hw = h_w
        self.range = range
        self.offset = offset
        self.default_contours = default_contours
        self.bbox = box(minx=(range + self.offset[0]), miny=(range + self.offset[1]),
                         maxx=self.hw[1]-(range-self.offset[0]), maxy=self.hw[0]-(range-self.offset[1]))
        self.cluster_objects = cluster_objects
        if self.cluster_objects:
            self.populate_with_clustering(points)
        else:
            self.points = self.populate(points)
        self.paths = []
        # self.max_end_bound = max_end_bound
    
    def update(self, contours = [], points = [], h_w = None, range = None):
        if contours:
            print("contours")
            self.contours = contours
        if h_w:
            print("h_w")
            self.hw = h_w
        if range:
            print("range")
            self.range = range
            self.bbox = box(minx=(range + self.offset[0]), miny=(range + self.offset[1]),
                         maxx=self.hw[1]-(range-self.offset[0]), maxy=self.hw[0]-(range-self.offset[1]))

        if self.cluster_objects:
            self.populate_with_clustering(points)
        else:
            self.points = self.populate(points)

    def populate (self, points):
        self.polygons = []
        contours = self.contours + [self.default_contours]
        for contour in contours:
            self.polygons.append(Polygon(contour))
            
        self.contours = self.reshape(contours)
        for point in points:
            self.contours.append([point])

    def extract_points_from_polygons(self, polygons):
        points_list = []
        for poly in polygons:
            # Extract exterior points of each polygon and convert them to integers
            exterior_points = [(int(x), int(y)) for x, y in poly.exterior.coords]
            points_list.append(exterior_points)
        return points_list
    
    def populate_with_clustering(self, points):
        self.polygons = []
        polygons = []
        contours = self.contours + [self.default_contours]
        # print(contours)
        for contour in contours:
            if contour:
                polygons.append(Polygon(contour))

        clustered_polygons = self.cluster_unite_polygons(polygons)

        self.polygons = clustered_polygons

        contours = self.extract_points_from_polygons(clustered_polygons)
            
        self.contours = self.reshape(contours)
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
    def get_outer_polygon(self, point):
        point = Point(point)
        for polygon in self.polygons:
            if point.within(polygon):
                return polygon
            
    def cluster_unite_polygons(self, polygons):
        final_polygons = []
        for i, polygon in enumerate(polygons):
            merged = False
            for j, final_polygon in enumerate(final_polygons):
                if polygon.intersects(final_polygon):
                    merged_polygon = unary_union([polygon, final_polygon])
                    final_polygons[j] = merged_polygon.convex_hull  # Convert to convex hull
                    merged = True
                    break
            if not merged:
                final_polygons.append(polygon.convex_hull)  # Convert to convex hull
        return final_polygons
    
        
    def move_point_outside_polygon(self, start, end, centroid, polygon, distance):
        closest_edge = self.closest_point(start, polygon)
        start_vector = (start[0]- centroid[0], start[1]- centroid[1])
        end_vector = (end[0] - centroid[0], end[1]- centroid[1])
        start_unit_vector = start_vector / np.linalg.norm(start_vector)
        end_unit_vector = end_vector / np.linalg.norm(end_vector)

        start_state = -1

        if start_unit_vector[0] >= 0 and start_unit_vector[1] >= 0:
            # bottom right
            start_state = 1
        elif start_unit_vector[0] < 0 and start_unit_vector[1] >= 0:
            # bottom left
            start_state = 2
        elif start_unit_vector[0] < 0 and start_unit_vector[1] < 0:
            # top left
            start_state = 3
        elif start_unit_vector[0] >= 0 and start_unit_vector[1] < 0:
            # top right
            start_state = 4

        new_state = -1

        if abs(end_unit_vector[0]) > abs(end_unit_vector[1]):
            # right
            if end_unit_vector[0] > 0:
                if start_state == 1 or start_state == 4:
                    # go right
                    new_state = 1
                elif start_state == 2:
                    # go bottom
                    new_state = 2
                elif start_state == 3:
                    # go top
                    new_state = 4
            # left
            else:
                if start_state == 2 or start_state == 3:
                    # go left
                    pass
                elif start_state == 1:
                    # go bottom
                    new_state = 2
                elif start_state == 4:
                    # go top
                    new_state = 4
        else:
            # bottom
            if end_unit_vector[1] > 0:
                if start_state == 1 or start_state == 2:
                    # go bottom
                    new_state = 2
                elif start_state == 3:
                    # go left
                    new_state = 3
                elif start_state == 4:
                    # go right
                    new_state = 1
            # top
            else:
                if start_state == 3 or start_state == 4:
                    # go top
                    new_state = 4
                elif start_state == 2:
                    # go left
                    new_state = 3
                elif start_state == 1:
                    # go right
                    new_state = 1

        new_point = (0,0)
        if new_state == 1:
            new_point = (closest_edge[0] + distance, start[1])
        elif new_state == 2:
            new_point = (start[0], closest_edge[1] + distance)
        elif new_state == 3:
            new_point = (closest_edge[0] - distance, start[1])
        elif new_state == 4:
            new_point = (start[0], closest_edge[1] - distance)

        return new_point

    def find_path (self, start, end):
        i = 0
        used_nodes = []
        if self.is_point_inside_any_polygon(end):
            pass
            # print("Error end is inside a contour")
            # raise("Error end is inside a contour")
        if self.is_point_inside_any_polygon(start):
            print("Start is inside a contour. This can cause an error")
            print("NEW POINT")
            polygon = self.get_outer_polygon(start)
            centroid = (int(polygon.centroid.x), int(polygon.centroid.y))
            polygon = [(int(x), int(y)) for x, y in polygon.exterior.coords]
            new_point = self.move_point_outside_polygon(start, end, centroid, polygon, 100)
            new_point = (int(new_point[0]), int(new_point[1]))
            _, new_point, was_outside = self.clip_line_to_bbox2(start, new_point)
            
            if was_outside:
                print("Outside")
                # new_point2 = self.get_close_point(polygon, centroid, start, end, 100)
                new_point2 = self.closest_point(start, polygon)
                new_point2 = self.move_outside(new_point2, centroid, 100)
                _, new_point2, _ = self.clip_line_to_bbox2(start, new_point2)
                start = [new_point2, [[start, new_point, new_point2]]]
            else:
                start = [new_point, [[start, new_point]]]
                pass
            used_nodes.append(start)
        else:
            start = [start, [[start]]]
            used_nodes.append(start)
        end = [end, []]

        for point in self.contours:
            point.append([])
            point.append(False)

        while used_nodes:
            check_crossing = True
            if i > 0:
                i -= 0
                check_crossing = False
                
            for node in used_nodes:
                self.make_pathes(node, end, check_crossing)
            
            used_nodes = []
            z = 0
            range = len(self.contours)
            while z < range:
                if self.contours[z][2]:
                    used_nodes.append(self.contours.pop(z))
                    range -= 1
                    z -= 1
                z += 1
        print("END")
        self.paths = end[1]

        return end[1]
    
    def get_outside_range(self, points, centroid, start):
        vector = ((start[0] - centroid[0]), (start[1] - centroid[1]))
        acceptable_points = []
        new_point1 = self.closest_point(start, points)
        for point in points:
            if ((vector[0] < 0 and point[0] < start[0]) or
                (vector[0] > 0 and point[0] > start[0]) or
                (vector[1] < 0 and point[1] < start[1]) or
                (vector[1] > 0 and point[1] > start[1])):
                new_point = self.move_outside(point, centroid, 100)
                start, new_point2, _ = self.clip_line_to_bbox(start, new_point)
                acceptable_points.append([new_point2, [[start, new_point1, new_point2]]])
        return acceptable_points
    
    # get a point closer to the end and to the start not intersecting the centroid
    def get_close_point(self, points, centroid, start, end, distance = 100):
        vector = ((start[0] - centroid[0]), (start[1] - centroid[1]))
        acceptable_points = []
        for point in points:
            if ((vector[0] < 0 and point[0] < start[0]) or
                (vector[0] > 0 and point[0] > start[0]) or
                (vector[1] < 0 and point[1] < start[1]) or
                (vector[1] > 0 and point[1] > start[1])):
                # new_point = self.move_outside(point, centroid, distance)
                acceptable_points.append(point)
        new_point = self.closest_point(end, acceptable_points)
        new_point = self.move_outside(new_point, centroid, distance)
        return new_point
    
    def move_outside(self, point, centroid, distance):
        start = np.array(centroid)
        end = np.array(point)
        direction = end - start
        direction_norm = direction / np.linalg.norm(direction)
        new_end_point = end + direction_norm * distance
        
        return (int(new_end_point[0]), int(new_end_point[1]))

    
    def closest_point(self, reference_point, points):
        # Initialize the minimum distance and the closest point
        min_distance = float('inf')
        closest_point = None

        # Iterate through each point in the set
        for point in points:
            # Calculate the Euclidean distance from the reference point
            distance = ((point[0] - reference_point[0]) ** 2 + (point[1] - reference_point[1]) ** 2) ** 0.5
            # Update the closest point and minimum distance if necessary
            if distance < min_distance:
                min_distance = distance
                closest_point = point

        return closest_point
    
    def unite_close_points(self, path, min_distance):
        new_path = [path[0]]
        for i in range(1, len(path)):
            # too risky, it can merge start point
            # midpoint = (int((path[i][0] + path[i+1][0]) / 2), int((path[i][1] + path[i+1][1]) / 2))
            # new_path.append(midpoint)
            if self.distance(path[i], path[i-1]) >= min_distance:
                new_path.append(path[i])

        return new_path
    
    def distance(self, point1, point2):
        return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    

    def project_point_onto_bbox(self, point):
        x, y = point
        minx, miny, maxx, maxy = self.bbox.bounds
        
        # Project onto the nearest edge
        if x < minx:
            x = minx
        elif x > maxx:
            x = maxx
        
        if y < miny:
            y = miny
        elif y > maxy:
            y = maxy
        
        return (x, y)

    def clip_line_to_bbox2(self, p1, p2):
        if Point(p1).within(self.bbox) and Point(p2).within(self.bbox):
            return [p1, p2, False]
        else:
            print("Project points")
            new_p1 = self.project_point_onto_bbox(p1)
            new_p2 = self.project_point_onto_bbox(p2)
            return [(int(new_p1[0]), int(new_p1[1])), (int(new_p2[0]), int(new_p2[1])), True]


    def make_pathes (self, start, end, check_crossing = True):
        if not self.check_path(start, end):
            for contour in self.contours:
                if self.check_path(start, contour, check_crossing):
                    contour[2] = True
        return

    def check_path (self, start, end, check_crossing = True):
        line = [start[0], end[0]]

        if check_crossing:
            if (self.is_line_crossing_any_polygon(line) or 
                self.is_line_intersecting_any_polygon(line) or 
                self.is_line_within_any_polygon(line)):
                return False
        for path in start[1]:
            new_path = path.copy()
            new_path.append(end[0])
            end[1].append(new_path)
        return True
    
    def find_shortest_path(self, min_distance = 150):
        lines = []
        if not self.paths:
            pass
            # print("Error: No path found.")
            # raise("Error: No path found.")
        for path in self.paths:
            lines.append([LineString(path).length, path])
        lines.sort(key=lambda x: x[0])
        short_path = lines[0][1]
        merged_path = self.unite_close_points(short_path, min_distance)
        return merged_path
    
    # def draw_graph (self):
    #     fig, ax = plt.subplots()

    #     for polygon in self.polygons:
    #         x, y = polygon.exterior.xy
    #         ax.fill(x, y, alpha=0.5)

    #     for path in self.paths:
    #         x, y = LineString(path).xy
    #         ax.plot(x, y, linewidth=2, label='Line')
        
    #     plt.show()

    # def draw_line (self, line):
    #     fig, ax = plt.subplots()

    #     for polygon in self.polygons:
    #         x, y = polygon.exterior.xy
    #         ax.fill(x, y, alpha=0.5)

    #     x, y = line.xy
    #     ax.plot(x, y, linewidth=2, label='Line')
        
    #     plt.show()

    #     return

