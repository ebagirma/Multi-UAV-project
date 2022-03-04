import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from shapely import geometry
class Planner(object):
    def __init__(self, polygons_start, d = 0.1, m = float('inf')):
        self.d = d
        self.m = m
        if m == float('inf') or m == 0:
            self.m = 10 ** 10
        self.horizontal = False
        if m == 0:
            self.horizontal = True
        self.polygon = []
        min_lat_point = float('inf')
        min_lng_point = float('inf')
        self.max_lng_point = (-float('inf'), -float('inf'))
        self.max_lat_point = (-float('inf'), -float('inf'))
        for point in polygons_start:
            if min_lat_point > point['lat']:
                min_lat_point = point['lat']
            if min_lng_point > point['lng']:
                min_lng_point = point['lng']


        self.min_lng_point = (float('inf'), float('inf'))
        self.min_lat_point = (float('inf'), float('inf'))

        for point in polygons_start:
            self.polygon += [(
                                100 * (point['lng'] - min_lng_point), 
                                100 * (point['lat'] - min_lat_point)
                            )]
            
            if self.max_lng_point[0] < self.polygon[-1][0]:
                self.max_lng_point = self.polygon[-1]
            if self.max_lat_point[1] < self.polygon[-1][1]:
                self.max_lat_point = self.polygon[-1]
            if self.min_lng_point[0] > self.polygon[-1][0]:
                self.min_lng_point = self.polygon[-1]
            if self.min_lat_point[1] > self.polygon[-1][1]:
                self.min_lat_point = self.polygon[-1]
        
        self.min_lng = min_lng_point
        self.min_lat = min_lat_point
        self.polygon_shapely = geometry.polygon.Polygon(self.polygon)

    @staticmethod  
    def y_intercept_m(x_intercept, m):
        b = -x_intercept * m
        return b
    
    @staticmethod
    def x_intercept_m(point, m):
        if m == 0: return float("inf")
        b = point[1] - point[0] * m
        return -b / m

    @staticmethod
    def line_intersection_point(a, b, c, d):
        print(a, b, c, d)
        if a[0] == b[0]:
            if d[0] == c[0]:
                return (float('inf'), float('inf'))
            else:
                m = (d[1] - c[1]) / (d[0] - c[0])
                y = m * a[0] + Planner.y_intercept_m(Planner.x_intercept_m(c, m), m)
                return (a[0], y)

        if d[0] == c[0]:
            m = (a[1] - b[1]) / (a[0] - b[0]) 
            y = c[0] * m +  Planner.y_intercept_m(Planner.x_intercept_m(a, m), m)
            return (c[0], y)
        m1 = (b[1] - a[1]) / (b[0] - a[0])
        m2 = (d[1] - c[1]) / (d[0] - c[0])
        
        if m1 == m2: return (float('inf'), float('inf'))
        x1 = Planner.x_intercept_m(a, m1)
        if x1 == float('inf'):
            b1 = a[1]
        else:
            b1 = Planner.y_intercept_m(x1, m1)
        x2 = Planner.x_intercept_m(c, m2)
        if x2 == float('inf'):
            b2 = c[1]
        else:
            b2 = Planner.y_intercept_m(x2, m2)
        x = (b2 - b1) / (m1 - m2)
        y = m1 * x + b1
        return (x, y)

    def x_intercept(self, point):
        b = point[1] - point[0] * self.m
        return -b / self.m

    def y_intercept(self, x_intercept):
        b = -x_intercept * self.m
        return b


    def is_in_polygon(self, point):
        if point[0] < 0 or point[1] < 0: return False
        if point[0] > self.max_lng_point[0]: return False
        if point[1] > self.max_lat_point[1]: return False
        if point[0] < self.min_lng_point[0]: return False
        if point[1] < self.min_lat_point[1]: return False
        return True
        # pt = geometry.Point(point)
        # return self.polygon_shapely.crosses(pt) or self.polygon_shapely.contains(pt)
         

    def plan(self):
        if self.horizontal:
            end_point = self.max_lat_point[1]
            
            y = -end_point

            path = []
            while y <= end_point:
                for point_ind in range(1, len(self.polygon)):
                    intersection = self.line_intersection_point(
                                                    (0, y), 
                                                    (1, y), 
                                                    self.polygon[point_ind - 1], 
                                                    self.polygon[point_ind])
                    if self.is_in_polygon(intersection):
                    # path += [(0, self.y_intercept(x))]
                    # path += [(x, 0)]
                        path += [intersection]
                intersection = self.line_intersection_point(
                                                    (0, y), 
                                                    (1, y), 
                                                    self.polygon[len(self.polygon) - 1], 
                                                    self.polygon[0])  
                if self.is_in_polygon(intersection):
                    path += [intersection]  
                y += self.d
            return path


        end_point = max(self.x_intercept(self.max_lat_point),  self.x_intercept(self.max_lng_point))
        
        x = -end_point - max(self.max_lat_point[1], self.max_lng_point[0])

        path = []
        while x <= end_point:
            for point_ind in range(1, len(self.polygon)):
                intersection = self.line_intersection_point(
                                                (x, 0), 
                                                (0, self.y_intercept(x)), 
                                                self.polygon[point_ind - 1], 
                                                self.polygon[point_ind])
                if self.is_in_polygon(intersection):
                # path += [(0, self.y_intercept(x))]
                # path += [(x, 0)]
                    path += [intersection]
            intersection = self.line_intersection_point(
                                                (x, 0), 
                                                (0, self.y_intercept(x)), 
                                                self.polygon[len(self.polygon) - 1], 
                                                self.polygon[0])  
            if self.is_in_polygon(intersection):
                path += [intersection]  
            x += self.d
        return path
    
    @staticmethod
    def separate_x_y(points):
        res_x = []
        res_y = []
        for point in points:
            res_x += [point[0]]
            res_y += [point[1]]
        return res_x, res_y

    def full_path(self):
        path = self.plan()
        path = [(p[0] / 100.0 + self.min_lng, p[1] / 100.0 + self.min_lat) for p in path]
        for i in range(1, len(path), 4):
            path[i], path[i - 1] = path[i - 1], path[i]
        return path

    def pretty(self):
        path = self.plan()
        print(path)
        # print(self.line_intersection_point(self.polygon[0], self.polygon[1], self.polygon[1], self.polygon[2]))
        # print(self.polygon)
        _, ax = plt.subplots()
        poly = Polygon(self.polygon, True)
        p = PatchCollection([poly])
        ax.add_collection(p)
        x, y = self.separate_x_y(path)
        plt.plot(x, y, 'ro')
        plt.show()
