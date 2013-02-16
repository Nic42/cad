#!/usr/bin/python
"""
G83 Z Q P R I K J F X* Y*
Z= Bottom of hole
Q= Peck amount 
P= Pause at bottom of hole
R= Position of the R &lt; clearance &gt; plane
I= Start peck amount
K= Amount to reduce each successive peck
J= Minimum peck amount
X and Y= Optional locations for successive holes.

"""
import argparse
from PIL import Image, ImageDraw

def get_main_color(img):
    colors = img.getcolors(img.size[0]*img.size[1])
    max_occurence, most_present = 0, 0
    for c in colors:
        if c[0] > max_occurence:
            (max_occurence, most_present) = c
    return most_present

def get_region_box(img,x,y):
    
    cell_width = img.size[0]/args.xdiv
    cell_height = img.size[1]/args.ydiv
    box = (
        x*cell_width,
        y*cell_height,
        x*cell_width+cell_width,
        y*cell_height+cell_height)
    return box

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="make a gcode file from a pic")

    parser.add_argument('--gcode', default="drill.ngc", help='gcode file to write', type=argparse.FileType('w'))
    parser.add_argument('--image', action='store', dest='image_file', help="image", required = True)
    parser.add_argument('--xdiv', action='store', dest='xdiv', type=int, default=5, help="xdiv")
    parser.add_argument('--ydiv', action='store', dest='ydiv', type=int, default=5, help="ydiv")
    parser.add_argument('--safez', action='store', dest='safez', type=float, default=5, help="z safety")
    parser.add_argument('--peck', action='store', dest='peck', type=float, default=0, help="peck")
    parser.add_argument('--feedspeed', action='store', dest='feedspeed', type=float, default=200, help="feedspeed mm/min")
    parser.add_argument('--depth', action='store', dest='z', type=float, default=5, help="z depth")
    parser.add_argument('--offset', action='store', dest='offset', type=float, default=2, help="offset z by this much")
    parser.add_argument('--flip', action='store_const', dest='flip', const=True, default=False, help="flip the image, making black white and vice versa")
    args = parser.parse_args()

    print "generating gcodes"
    gcodes = []
    #preamble
    gcode = []
    gcode.append( 'G17 G21 G90 G64 P0.003 M3 S3000 M7')
    gcode.append( 'G0 Z%.4f F%s' %(float(args.safez), float(args.feedspeed)) )


    src = Image.open(args.image_file)
    src = src.convert('L')
    drill = Image.new('L',src.size)
    draw = ImageDraw.Draw(drill)
    firstHole = False
#    im.show()
    (x,y) = src.size
    for i in range(args.xdiv):
        for j in range(args.ydiv):
            box = get_region_box(src,i,j)
            region = src.crop(box)
            main_color = get_main_color(region)
            z = float(args.z / 255.0) * main_color
            if args.flip:
                z = args.z - z
            if args.offset:
                z = z + args.offset

            print z

            #draw a representative image
            draw.rectangle(box, fill=main_color)

            #if peck
            peck = args.peck
            if peck == 0:
                peck = args.safez - - z

            gcode.append( 'G83 X%.4f Y%.4f Z%.4f Q%.4f R%.4f' %( 
                box[0],
                box[1],
                -z,
                float(peck),
                float(args.safez)))

    drill.save("drill.png")
    gcode.append( 'M5 M9 M2' )
    for item in gcode:
      args.gcode.write("%s\n" % item)