import torch
from shapely.geometry import LineString, Polygon, Point, box

class Path_Finder:
    def __init__(self, offset, contours=[], default_contours=[], points=[], h_w=None, range=200):
        self.contours = contours
        self.hw = h_w
        self.range = range
        self.offset = offset
        self.default_contours = default_contours
        self.bbox = box(minx=(range + self.offset[0]), miny=(range + self.offset[1]),
                        maxx=self.hw[1] - (range - self.offset[0]), maxy=self.hw[0] - (range - self.offset[1]))
        self.points = self.populate(points)

    def update(self, contours=[], points=[], h_w=None, range=None):
        if contours:
            self.contours = contours
        if h_w:
            self.hw = h_w
        if range:
            self.range = range
            self.bbox = box(minx=(range + self.offset[0]), miny=(range + self.offset[1]),
                            maxx=self.hw[1] - (range - self.offset[0]), maxy=self.hw[0] - (range - self.offset[1]))
        self.points = self.populate(points)

    def populate(self, points):
        self.polygons = []
        contours = self.contours + self.default_contours
        for contour in contours:
            self.polygons.append(Polygon(contour))

        self.contours = self.reshape(contours)
        for point in points:
            self.contours.append([point])

    def reshape(self, contours):
        new_contours = []
        for contour in contours:
            contour_tensor = torch.tensor(contour, dtype=torch.float32)
            mask = torch.logical_and(
                torch.logical_and(contour_tensor[:, 0] > self.range, contour_tensor[:, 1] > self.range),
                torch.logical_and(contour_tensor[:, 0] < self.hw[1] - self.range, contour_tensor[:, 1] < self.hw[0] - self.range)
            )
            new_contours.extend(contour_tensor[mask].tolist())
        return new_contours

    def is_point_inside_any_polygon(self, point):
        point_tensor = torch.tensor(point, dtype=torch.float32)
        polygons_tensor = torch.stack([torch.tensor(polygon.exterior.coords, dtype=torch.float32) for polygon in self.polygons])

        diff = polygons_tensor - point_tensor
        cross_products = diff[:, :-1, 0] * diff[:, 1:, 1] - diff[:, :-1, 1] * diff[:, 1:, 0]
        winding_numbers = torch.sum(torch.sign(cross_products), dim=-1)

        return torch.any(winding_numbers != 0).item()

    def find_path(self, start, end):
        if self.is_point_inside_any_polygon(start):
            polygon = self.get_outer_polygon(start)
            centroid = torch.tensor(polygon.centroid.coords[0], dtype=torch.float32)
            polygon_coords = torch.tensor(polygon.exterior.coords, dtype=torch.float32)
            new_point = self.move_point_outside_polygon(start, end, centroid, polygon_coords, 100)
            new_point = (int(new_point[0]), int(new_point[1]))
            start_tensor, new_point_tensor, was_outside = self.clip_line_to_bbox2(start, new_point)
            
            if was_outside:
                new_point2 = self.closest_point(start, polygon_coords)
                new_point2 = self.move_outside(new_point2, centroid, 100)
                _, new_point2, _ = self.clip_line_to_bbox2(start, new_point2)
                start_points = torch.tensor([new_point2], dtype=torch.float32)
                start_paths = [[[new_point2.tolist(), new_point_tensor.tolist(), new_point.tolist(), start]]]
            else:
                start_points = torch.tensor([new_point_tensor], dtype=torch.float32)
                start_paths = [[[start, new_point]]]
        else:
            start_points = torch.tensor([start], dtype=torch.float32)
            start_paths = [[[start]]]

        end_point = torch.tensor(end, dtype=torch.float32)
        end_paths = []

        contours_tensor = torch.tensor(self.contours, dtype=torch.float32)

        while len(start_points) > 0:
            num_points = len(start_points)
            num_contours = len(contours_tensor)

            # Generate paths in parallel
            start_points_expanded = start_points.unsqueeze(1).expand(num_points, num_contours, 2)
            contours_expanded = contours_tensor.unsqueeze(0).expand(num_points, num_contours, 2)
            paths = torch.stack([start_points_expanded, contours_expanded], dim=2)

            # Check path validity in parallel
            valid_paths = self.check_path_batch(paths, end_point)

            # Update path data based on validity
            for i in range(num_points):
                for j in range(num_contours):
                    if valid_paths[i, j]:
                        for path in start_paths[i]:
                            new_path = path + [contours_tensor[j].tolist()]
                            if torch.all(contours_tensor[j] == end_point):
                                end_paths.append(new_path)
                            else:
                                contours_tensor[j][2] = True

            # Prepare for the next iteration
            start_points = contours_tensor[contours_tensor[:, 2] == True, :2]
            start_paths = [[path + [point.tolist()] for path in start_paths[i]] for i, point in enumerate(start_points)]
            contours_tensor = contours_tensor[contours_tensor[:, 2] == False]

        self.paths = end_paths
        return end_paths

    def check_path_batch(self, paths, check_crossing=True):
        start_points = paths[:, :, 0]
        end_points = paths[:, :, 1]

        # Check if paths intersect any polygons
        polygons_tensor = torch.stack([torch.tensor(polygon.exterior.coords, dtype=torch.float32) for polygon in self.polygons])
        num_paths, num_points, _ = paths.shape
        num_polygons, num_polygon_points, _ = polygons_tensor.shape
        
        paths_expanded = paths.view(num_paths, num_points, 1, 1, 2).expand(num_paths, num_points, num_polygons, num_polygon_points, 2)
        polygons_expanded = polygons_tensor.view(1, 1, num_polygons, num_polygon_points, 2).expand(num_paths, num_points, num_polygons, num_polygon_points, 2)
        
        diff = polygons_expanded - paths_expanded
        cross_products = diff[:, :, :, :-1, 0] * diff[:, :, :, 1:, 1] - diff[:, :, :, :-1, 1] * diff[:, :, :, 1:, 0]
        sign_changes = torch.sign(cross_products[:, :, :, :-1]) != torch.sign(cross_products[:, :, :, 1:])
        intersects = torch.any(sign_changes, dim=-1)
        path_intersects = torch.any(intersects, dim=0)

        # Check if paths cross any polygons
        if check_crossing:
            start_points_expanded = start_points.view(num_paths, num_points, 1, 2).expand(num_paths, num_points, num_polygons, 2)
            end_points_expanded = end_points.view(num_paths, num_points, 1, 2).expand(num_paths, num_points, num_polygons, 2)
            polygons_expanded_crossing = polygons_tensor.view(1, 1, num_polygons, num_polygon_points, 2).expand(num_paths, num_points, num_polygons, num_polygon_points, 2)
            
            path_crosses = torch.any(torch.logical_and(
                torch.any(start_points_expanded.unsqueeze(-2) != polygons_expanded_crossing, dim=-1),
                torch.any(end_points_expanded.unsqueeze(-2) != polygons_expanded_crossing, dim=-1)
            ), dim=0)
        else:
            path_crosses = torch.zeros_like(path_intersects)

        # Check if paths are within any polygons
        diff_start = polygons_expanded - start_points.view(num_paths, num_points, 1, 1, 2).expand(num_paths, num_points, num_polygons, num_polygon_points, 2)
        diff_end = polygons_expanded - end_points.view(num_paths, num_points, 1, 1, 2).expand(num_paths, num_points, num_polygons, num_polygon_points, 2)
        cross_products_start = diff_start[:, :, :, :-1, 0] * diff_start[:, :, :, 1:, 1] - diff_start[:, :, :, :-1, 1] * diff_start[:, :, :, 1:, 0]
        cross_products_end = diff_end[:, :, :, :-1, 0] * diff_end[:, :, :, 1:, 1] - diff_end[:, :, :, :-1, 1] * diff_end[:, :, :, 1:, 0]
        winding_numbers_start = torch.sum(torch.sign(cross_products_start), dim=-1)
        winding_numbers_end = torch.sum(torch.sign(cross_products_end), dim=-1)
        path_within = torch.any(torch.logical_and(winding_numbers_start != 0, winding_numbers_end != 0), dim=0)

        # Combine the validity checks
        valid_paths = torch.logical_not(torch.logical_or(torch.logical_or(path_intersects, path_crosses), path_within))

        return valid_paths

    def get_outer_polygon(self, point):
        point = Point(point)
        for polygon in self.polygons:
            if point.within(polygon):
                return polygon

    def move_point_outside_polygon(self, start, end, centroid, polygon, distance):
        start_tensor = torch.tensor(start, dtype=torch.float32)
        end_tensor = torch.tensor(end, dtype=torch.float32)
        
        start_vector = start_tensor - centroid
        end_vector = end_tensor - centroid
        start_unit_vector = start_vector / torch.norm(start_vector)
        end_unit_vector = end_vector / torch.norm(end_vector)

        start_state = -1

        if start_unit_vector[0] >= 0 and start_unit_vector[1] >= 0:
            start_state = 1
        elif start_unit_vector[0] < 0 and start_unit_vector[1] >= 0:
            start_state = 2
        elif start_unit_vector[0] < 0 and start_unit_vector[1] < 0:
            start_state = 3
        elif start_unit_vector[0] >= 0 and start_unit_vector[1] < 0:
            start_state = 4

        new_state = -1

        if torch.abs(end_unit_vector[0]) > torch.abs(end_unit_vector[1]):
            if end_unit_vector[0] > 0:
                if start_state == 1 or start_state == 4:
                    new_state = 1
                elif start_state == 2:
                    new_state = 2
                elif start_state == 3:
                    new_state = 4
            else:
                if start_state == 2 or start_state == 3:
                    pass
                elif start_state == 1:
                    new_state = 2
                elif start_state == 4:
                    new_state = 4
        else:
            if end_unit_vector[1] > 0:
                if start_state == 1 or start_state == 2:
                    new_state = 2
                elif start_state == 3:
                    new_state = 3
                elif start_state == 4:
                    new_state = 1
            else:
                if start_state == 3 or start_state == 4:
                    new_state = 4
                elif start_state == 2:
                    new_state = 3
                elif start_state == 1:
                    new_state = 1

        closest_edge = self.closest_point(start, polygon)
        new_point = torch.zeros(2)
        if new_state == 1:
            new_point[0] = closest_edge[0] + distance
            new_point[1] = start_tensor[1]
        elif new_state == 2:
            new_point[0] = start_tensor[0]
            new_point[1] = closest_edge[1] + distance
        elif new_state == 3:
            new_point[0] = closest_edge[0] - distance
            new_point[1] = start_tensor[1]
        elif new_state == 4:
            new_point[0] = start_tensor[0]
            new_point[1] = closest_edge[1] - distance

        return new_point

    def closest_point(self, reference_point, points):
        reference_point_tensor = torch.tensor(reference_point, dtype=torch.float32)
        points_tensor = torch.tensor(points, dtype=torch.float32)
        distances = torch.norm(points_tensor - reference_point_tensor, dim=-1)
        closest_index = torch.argmin(distances)
        return points[closest_index]

    def move_outside(self, point, centroid, distance):
        start = torch.tensor(centroid, dtype=torch.float32)
        end = torch.tensor(point, dtype=torch.float32)
        direction = end - start
        direction_norm = direction / torch.norm(direction)
        new_end_point = end + direction_norm * distance
        return new_end_point.tolist()

    def clip_line_to_bbox2(self, p1, p2):
        p1_tensor = torch.tensor(p1, dtype=torch.float32)
        p2_tensor = torch.tensor(p2, dtype=torch.float32)
        bbox_tensor = torch.tensor(self.bbox.bounds, dtype=torch.float32)

        if torch.all(p1_tensor >= bbox_tensor[:2]) and torch.all(p1_tensor <= bbox_tensor[2:]) and \
           torch.all(p2_tensor >= bbox_tensor[:2]) and torch.all(p2_tensor <= bbox_tensor[2:]):
            return [p1, p2, False]
        else:
            new_p1 = torch.clamp(p1_tensor, bbox_tensor[:2], bbox_tensor[2:])
            new_p2 = torch.clamp(p2_tensor, bbox_tensor[:2], bbox_tensor[2:])
            return [new_p1.tolist(), new_p2.tolist(), True]

    def make_pathes(self, start, end, check_crossing=True):
        if not self.check_path_batch(torch.tensor([[start[0], end[0]]], dtype=torch.float32), check_crossing=check_crossing):
            contours_tensor = torch.tensor(self.contours, dtype=torch.float32)
            start_tensor = torch.tensor(start[0], dtype=torch.float32)
            valid_contours = self.check_path_batch(torch.stack([start_tensor.expand(len(contours_tensor), 2), contours_tensor[:, 0]], dim=1), check_crossing=check_crossing)
            for i in range(len(self.contours)):
                if valid_contours[i]:
                    self.contours[i][2] = True

    def find_shortest_path(self, min_distance=150):
        lengths = torch.tensor([LineString(path).length for path in self.paths])
        shortest_index = torch.argmin(lengths)
        short_path = self.paths[shortest_index.item()]

        short_path_tensor = torch.tensor(short_path, dtype=torch.float32)
        diff = short_path_tensor.unsqueeze(0) - short_path_tensor.unsqueeze(1)
        distances = torch.norm(diff, dim=-1)
        mask = distances >= min_distance
        mask[torch.arange(len(short_path)), torch.arange(len(short_path))] = True
        merged_path = short_path_tensor[torch.any(mask, dim=-1)].tolist()

        return merged_path