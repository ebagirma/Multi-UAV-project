# def line_intersection_point(a, b, c, d):
#         if a == c or a == d:
#             return a 
#         if b == c or b == d:
#             return b
#         a1 = b[1] - a[1]
#         b1 = a[1] - b[1]
#         c1 = a1 * a[0] + b1 * a[1]

#         a2 = d[1] - c[1]
#         b2 = c[0] - d[0]
#         c2 = a2 * c[0] - b2 * c[1]

#         determinant = a1 * b2 - a2 * b1
#         if determinant == 0: return (float('inf'), float('inf'))
#         x = (b2 * c1 - b1 * c2) / determinant
#         y = (a1 * c2 + a2 * c1) / determinant
#         return (x, y)

def y_intercept_m(x_intercept, m):
    b = -x_intercept * m
    return b

def x_intercept_m(point, m):
    if m == 0:
        return float("inf")
    b = point[1] - point[0] * m
    return -b / m

def line_intersection_point(a, b, c, d):
    if a[0] == b[0]:
        if d[0] == c[0]:
            return (float('inf'), float('inf'))
        else:
            m = (d[1] - c[1]) / (d[0] - c[0])
            y = m * a[0] + y_intercept_m(x_intercept_m(c, m), m)
            return (a[0], y)

    if d[0] == c[0]:
        m = (a[1] - b[1]) / (a[0] - b[0]) 
        y = c[0] * m +  y_intercept_m(x_intercept_m(a, m), m)
        return (c[0], y)
    m1 = (b[1] - a[1]) / (b[0] - a[0])
    m2 = (d[1] - c[1]) / (d[0] - c[0])
    
    if m1 == m2: return (float('inf'), float('inf'))
    x1 = x_intercept_m(a, m1)
    if x1 == float('inf'):
        b1 = a[1]
    else:
        b1 = y_intercept_m(x1, m1)
    x2 = x_intercept_m(c, m2)
    if x2 == float('inf'):
        b2 = c[1]
    else:
        b2 = y_intercept_m(x2, m2)
    x = (b2 - b1) / (m1 - m2)
    y = m1 * x + b1
    return (x, y)


print(line_intersection_point((50.0, 10.0), (32.0, 32.0), (0.0, 40.0), (35.0, 40.0)))
