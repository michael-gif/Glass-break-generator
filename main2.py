from PIL import Image, ImageDraw
import random
import math

class Line:
    def __init__(self, dimensions, breakage_points_per_line, break_point, edge_point):
        self.dimensions = dimensions
        self.breakage_points_per_line = breakage_points_per_line
        self.break_point = break_point
        self.edge_point = edge_point
        self.line_points = []
        #self.line_points = self.get_line_points(break_point, edge_point, breakage_points_per_line)
        self.normals = []

    def get_line_points(self, start, end, break_points):
        points = [start]
        diff_x = end[0] - start[0]
        diff_y = end[1] - start[1]
        magnitude = math.sqrt(diff_x ** 2 + diff_y ** 2)
        point_spacing = (magnitude / (break_points + 1)) / random.uniform(1, 2)
        for i in range(1, break_points + 1, 1):
            point_spacing *= 1.05
            scale_factor = point_spacing / magnitude
            spacing_x = diff_x * scale_factor
            spacing_y = diff_y * scale_factor
            points.append((start[0] + (i * spacing_x), start[1] + (i * spacing_y)))
        points.append(end)
        return points

    def get_normal_lines(self, edge_point, edge_point2, break_point, number_of_normals):
        normal_lines = []
        # calculate normal gradient for edge_point
        gradient = self.get_gradient(edge_point, break_point)
        if gradient == None:
            return
        normal_gradient = -1/gradient
        
        # get equation for edge_point2
        gradient2 = self.get_gradient(edge_point2, break_point)
        if gradient == None:
            return
        y_intercept2 = edge_point2[1] - (gradient2 * edge_point2[0])

        # get line points for edge_point
        self.line_points = self.get_line_points(break_point, edge_point, number_of_normals)

        # get intersection coord between normal line and second line for each point on line
        for i in range(1, len(self.line_points) - 1):
            point = self.line_points[i]
            y_intercept = point[1] - (normal_gradient * point[0])

            # find intersection point between normal and second line
            new_x = (gradient * (y_intercept2 - y_intercept)) / (-1 - (gradient2 * gradient))
            new_y = (gradient2 * new_x) + y_intercept2
            new_point = (new_x, new_y)

            # move point and new point along normals by variation to change shape of region
            variation = random.randint(1, 10)
            diff_x = new_point[0] - point[0]
            diff_y = new_point[1] - point[1]
            magnitude = math.sqrt(diff_x ** 2 + diff_y ** 2)
            scale_factor = variation / magnitude
            scale_x = diff_x * scale_factor
            scale_y = diff_y * scale_factor
            altered_point = (point[0] + scale_x, point[1] + scale_y)
            self.line_points[i] = altered_point
            normal_lines.append([altered_point, new_point])

        return normal_lines

    def get_gradient(self, a, b):
        x = b[0] - a[0]
        y = b[1] - a[1]
        try:
            return y / x
        except:
            return None
        
def get_edge_points(dimensions, breakage_lines, break_point):
    perimeter = (dimensions[0] * 2) + (dimensions[1] * 2)
    
    # generate evenly spaced points
    edge_points = [a * (perimeter / breakage_lines) for a in range(breakage_lines)]
    print(f"Generated {breakage_lines} equally spaced edge points")

    # vary points by a few pixels
    for x in range(len(edge_points)):
        direction = -1 if random.randint(0,1) == 0 else 1
        if direction == -1:
            edge_points[x] -= random.randint(1,20)
        else:
            edge_points[x] += random.randint(1,20)
    print("Added a variation between 1 and 20 pixels to each edge point")

    # shift points by random amount in random direction
    direction = -1 if random.randint(0,1) == 0 else 1
    offset = random.randint(1, breakage_lines)
    if direction == -1:
        offset *= -1
    for x in range(len(edge_points)):
        edge_points[x] += offset
    print(f"Offset all edge points by {offset} pixels")

    # move negative values to end of list
    for point in edge_points:
        if point < 0:
            edge_points.append(perimeter + edge_points.pop(0))
    print("Converted all negative edge points to positive points")

    # put point into edge lists
    top_edge = []
    right_edge = []
    bottom_edge = []
    left_edge = []
    for point in edge_points:
        if point >= 0 and point < dimensions[0]:
            top_edge.append(point)
        elif point >= dimensions[0] and point < dimensions[0] + dimensions[1]:
            right_edge.append(point)
        elif point >= dimensions[0] + dimensions[1] and point < (dimensions[0] * 2) + dimensions[1]:
            bottom_edge.append(point)
        else:
            left_edge.append(point)
    print("Put all points into 4 edge lists")

    # convert each edge point into a coordinate
    for i in range(len(top_edge)):
        top_edge[i] = (top_edge[i], 0)
    for i in range(len(right_edge)):
        right_edge[i] = (dimensions[0], right_edge[i] - dimensions[0])
    for i in range(len(bottom_edge)):
        bottom_edge[i] = (dimensions[0] - (bottom_edge[i] - dimensions[0] - dimensions[1]), dimensions[1])
    for i in range(len(left_edge)):
        left_edge[i] = (0, dimensions[1] - (left_edge[i] - (dimensions[0] * 2) - dimensions[1]))
    print("Converted all edge points to coordinates")

    edges = [top_edge, right_edge, bottom_edge, left_edge]
    return edges

def main():
    dimensions = (1000, 1000)
    breakage_lines = 50
    breakage_points_per_line = 20
    break_point = (500, 500)
    line_color = 'black'
    im = Image.new('RGB', dimensions, (255, 255, 255))
    draw = ImageDraw.Draw(im)

    edge_points = get_edge_points(dimensions, breakage_lines, break_point)   
    lines = [Line(dimensions, breakage_points_per_line, break_point, edge_point) for edge in edge_points for edge_point in edge]
    
    points = [point for edge in edge_points for point in edge]
    points.append(points[0])
    for i in range(len(points) - 1):
        lines[i].normals = lines[i].get_normal_lines(points[i], points[i + 1], break_point, breakage_points_per_line)

    # draw normal lines for each breakage line
    for line in lines:
        for normal in line.normals:
            draw.line(normal, fill=line_color)

    # draw lines emitting from break point
    for line in lines:
        for i in range(len(line.line_points) - 2):
            draw.line([line.line_points[i], line.line_points[i + 1]], fill='black')
    im.save('output.png')

if __name__ == '__main__':
    main()
