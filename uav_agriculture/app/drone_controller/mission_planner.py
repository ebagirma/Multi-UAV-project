import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import matplotlib.path as mpltPath
import numpy as np
from functools import reduce
import operator
import math

class LineSegment(object):
    def __init__(self, x0, y0, x1, y1):
        self.x0 = x0
        self.x1 = x1
        self.y0 = y0
        self.y1 = y1

        self.m = float('inf')
        try:
            self.m = (y1 - y0) / (x1 - x0)
        except ZeroDivisionError:
            pass
        self.b = y1 - self.m * x1

    def __str__(self):
        return "Line Object with m=%f and b=%f; End points at (%f, %f) and (%f, %f)" % (self.m, self.b, self.x0, self.y0, self.x1, self.y1)
    def __repr__(self):
        return "Line Object with m=%f and b=%f; End points at (%f, %f) and (%f, %f)" % (self.m, self.b, self.x0, self.y0, self.x1, self.y1)
        


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
        min_lng_index = 0
        for i, point in enumerate(polygons_start):
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
            if self.min_lat_point[1] >= self.polygon[-1][1]:
                self.min_lat_point = self.polygon[-1]
                min_lng_index = i

        newPoly = [[0, 0] for i in self.polygon]
        for i in range(len(self.polygon)):
            newPoly[((i + 1) + min_lng_index) % len(self.polygon)] = self.polygon[i]
        self.polygon = newPoly
        
        self.min_lng = min_lng_point
        self.min_lat = min_lat_point
        # self.polygon_shapely = geometry.polygon.Polygon(self.polygon)
        self.lines = self.generateLines()
        # print(self.lines)
        coords = self.polygon
        # center = tuple(map(operator.truediv, reduce(lambda x, y: map(operator.add, x, y), coords), [len(coords)] * 2))
        # self.polygon = sorted(coords, key=lambda coord: (-15 - math.degrees(math.atan2(*tuple(map(operator.sub, coord, center))[::-1]))) % 60)


    @staticmethod  
    def y_intercept_m(x_intercept, m):
        b = -x_intercept * m
        return b


    @staticmethod  
    def calc_slope(x0, y0, x1, y1):
        m = float('inf')
        try:
            m = (y1 - y0) / (x1 - x0)
        except ZeroDivisionError:
            pass
        return m

    @staticmethod
    def x_intercept_m(point, m):
        if m == 0: return float("inf")
        b = point[1] - point[0] * m
        return -b / m

    @staticmethod
    def line_intersection_point(a, b, c, d):
        # print(a, b, c, d)
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
        # print(self.lines)
        if point[0] < 0 or point[1] < 0: return False
        if point[0] > self.max_lng_point[0]: return False
        if point[1] > self.max_lat_point[1]: return False
        if point[0] < self.min_lng_point[0]: return False
        if point[1] < self.min_lat_point[1]: return False
        

        lines = self.lines
        ret = False
        for line in lines:
            rxi, ryi = round(point[0], 4), round(point[1], 4)
            rx0, rx1 = round(line.x0, 4), round(line.x1, 4)
            ry0, ry1 = round(line.y0, 4), round(line.y1, 4)
            # print (line.m)
            if line.m == float('inf'):
                # print("\t", (rxi, ryi), (rx0, rx1))
                # print()
                ret = ret or (rx0 == rxi and rxi == rx1 and ((ry0 <= ryi <= ry1) or (ry1 <= ryi <= ry0)))
            else:
                # print("\t1.", round(point[1], 5), round(point[0] * line.m + line.b, 5))
                # print("\t2.", (line.x0, point[0], line.x1))
                # print("\t3.", (line.y0, point[1], line.y1))
                xs = (rx0 <= rxi <= rx1) or (rx1 <= rxi <= rx0)
                ys = (ry0 <= ryi <= ry1) or (ry1 <= ryi <= ry0)
                # if line.m == 0 and rx0 <= rxi<= rx1:
                #     print(rxi, ryi, rx0, ry0, rx1, ry1)
                #     return True
                ret = ret or (ryi == round(point[0] * line.m + line.b, 4) and xs and ys)
        return ret
        # path = mpltPath.Path(self.polygon)
        # return path.contains_points([point])

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

        if self.m >= 0:
            x = -abs(self.m * self.max_lat_point[1]) if self.m < 10000 else self.d
            end_point = self.max_lng_point[0] 
        else:
            x = 0
            end_point = self.max_lng_point[0] + abs(self.m * self.max_lat_point[1])
        # print(end_point, x)

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

    def generateLines(self):
        lines = []
        for p in range(1, len(self.polygon)):
            x1, y1 = self.polygon[p]
            x0, y0 = self.polygon[p - 1]
            lines.append(LineSegment(x0, y0, x1, y1))
        if len(self.polygon) >= 2:
            x1, y1 = self.polygon[0]
            x0, y0 = self.polygon[len(self.polygon) - 1]
            lines.append(LineSegment(x0, y0, x1, y1))
        return lines

    # def plan1(self):
    #     start = [0, 0]
    #     lines = self.generateLines()
    #     path = []
    #     for point in self.polygon:
    #         x1, y1 = point
    #         x0, y0 = start
    #         m_c = Planner.calc_slope(x0, y0, x1, y1)
    #         if m_c == self.m:
    #             path.append(point)
            
    #     return path
    
    @staticmethod
    def separate_x_y(points):
        res_x = []
        res_y = []
        for point in points:
            res_x += [point[0]]
            res_y += [point[1]]
        return res_x, res_y
        
    @staticmethod
    def orderPath(path):
        for i in range(1, len(path), 4):
            path[i], path[i - 1] = path[i - 1], path[i]
        return path

    def full_path(self, lat=None, lon=None):
        path = self.plan()
        if lat == None:
            lat = self.min_lat_point[1]
        if lon == None:
            lon = self.min_lng_point[0]
        # print(lat, lon)
        # print("Path", path)

        path = [(p[0] / 100.0 + lon, p[1] / 100.0 + lat) for p in path]
        path = Planner.orderPath(path)

        # curr = -1
        # finalPath = []
        # for i in range(1, len(path)):
        #     m = Planner.calc_slope(path[i - 1][0], path[i - 1][1], path[i][0], path[i][1])
        #     if m != curr:
        #         finalPath.append(path[i])
        #         curr = m
        

        # print(path)
        return path

    def pretty(self):
        path = Planner.orderPath(self.plan())
        # print(path)
        # print(self.line_intersection_point(self.polygon[0], self.polygon[1], self.polygon[1], self.polygon[2]))
        # print(self.polygon)
        _, ax = plt.subplots()
        poly = Polygon(self.polygon, True)
        p = PatchCollection([poly])
        ax.add_collection(p)
        # print(path)
        x, y = self.separate_x_y(path)
        # C = np.array([[255, 0, 0], [0, 255, 0], [0, 0, 255]])

        plt.scatter(x, y, color='r', zorder=2)

        plt.plot(x, y, color='y', zorder=1)
        plt.show()
        return path