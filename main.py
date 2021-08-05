from PIL import Image, ImageDraw
import random
import math
        
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

def get_line_points(start, end, break_points):
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

def get_normal_lines(edges, break_point, number_of_normals):
    points = []
    for edge in edges:
        for point in edge:
            points.append(point)
    points.append(points[0])
    
    normal_lines = []
    for i in range(len(points) - 1):
        # calculate normal gradient for edge point
        point = points[i]
        diff_x = break_point[0] - point[0]
        diff_y = break_point[1] - point[1]
        if diff_x == 0 or diff_y == 0:
            continue
        gradient = diff_y / diff_x
        normal_gradient = -1/gradient
        
        # get equation for next line
        point = points[i + 1]
        diff_x = break_point[0] - point[0]
        diff_y = break_point[1] - point[1]
        if diff_x == 0 or diff_y == 0:
            continue
        gradient2 = diff_y / diff_x
        y_intercept2 = point[1] - (gradient2 * point[0])

        line_points = get_line_points(break_point, points[i], number_of_normals)
        
        # get intersection coord between normal line and second line for each point on line
        for i in range(len(line_points) - 1):
            point = line_points[i]
            y_intercept = point[1] - (normal_gradient * point[0])
            #draw.line([point, (100, (100 * normal_gradient) + y_intercept)], fill='green')
            #draw.line([break_point, (point[0], (point[0] * gradient2) + y_intercept2)], fill='blue')

            new_x = (gradient * (y_intercept2 - y_intercept)) / (-1 - (gradient2 * gradient))
            new_y = (gradient2 * new_x) + y_intercept2
            new_point = (new_x, new_y)
            normal_lines.append([point, new_point])
            #draw.ellipse([new_point, (new_point[0] + 1, new_point[1] + 1)], fill='green')

    print(f"Generated {number_of_normals} lines between all the breakage lines")
    return normal_lines

def main():
    dimensions = (1000, 1000)
    breakage_lines = 50
    breakge_points_per_line = 20
    break_point = (500, 500)
    line_color = 'black'

    edge_points = get_edge_points(dimensions, breakage_lines, break_point)

    im = Image.new('RGB', dimensions, (255, 255, 255))
    draw = ImageDraw.Draw(im)
    # draw lines from break_point to each edge point
    for edge in edge_points:
        for point in edge:
            draw.line([break_point, point], fill=line_color)
    # draw lines for each break point on each line
    for line in get_normal_lines(edge_points, break_point, breakge_points_per_line):
        draw.line(line, fill=line_color)
    im.save('output.png')

if __name__ == '__main__':
    main()
