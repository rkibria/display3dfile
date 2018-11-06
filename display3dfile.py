import sys, pygame, math, argparse

import matrix_ops, obj_file, draw3d_ops

parser = argparse.ArgumentParser()
parser.add_argument("filename", help="path to .obj or .dat (Bezier data) file")
args = parser.parse_args()

#####

pygame.init()

#####

size = width, height = 1000, 800
o_x = width/2
o_y = height/2

# Define the colors we will use in RGB format
BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
BLUE =  (  0,   0, 255)
GREEN = (  0, 255,   0)
RED =   (255,   0,   0)

screen = pygame.display.set_mode(size)

####

pygame.display.set_caption("File: %s" % args.filename)

originalObj = obj_file.loadFile(args.filename)

#Loop until the user clicks the close button.
done = False
clock = pygame.time.Clock()

sc = 0.3
scaleM = matrix_ops.getScaleMatrix(sc, sc, sc)

tx = 0.0
ty = 0.0
tz = 0.0
translM = matrix_ops.getTranslationMatrix(tx, ty, tz)

rx = 0.0
rotxM = matrix_ops.getRotateXMatrix(rx)

ry = 0.0
rotyM = matrix_ops.getRotateYMatrix(ry)

rz = 0.0
rotzM = matrix_ops.getRotateZMatrix(rz)

drot = math.pi / 180.0 * 5

fontSize = 20
font = pygame.font.Font(None, fontSize)

while not done:
        # This limits the while loop to a max of 10 times per second.
        # Leave this out and we will use all CPU we can.
        clock.tick(10)

        viewChanged = False
        for event in pygame.event.get(): # User did something
                if event.type == pygame.QUIT: # If user clicked close
                        done=True # Flag that we are done so we exit this loop
                elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_LEFT:
                                viewChanged = True
                                tx += -1.0
                        elif event.key == pygame.K_RIGHT:
                                viewChanged = True
                                tx += 1.0

                        elif event.key == pygame.K_UP:
                                viewChanged = True
                                ty += 1.0
                        elif event.key == pygame.K_DOWN:
                                viewChanged = True
                                ty += -1.0

                        elif event.key == pygame.K_q:
                                viewChanged = True
                                tz += 1.0
                        elif event.key == pygame.K_a:
                                viewChanged = True
                                tz += -1.0

                        elif event.key == pygame.K_w:
                                viewChanged = True
                                sc += 0.1
                        elif event.key == pygame.K_s:
                                if sc >= 0.2:
                                        viewChanged = True
                                        sc += -0.1

                        elif event.key == pygame.K_e:
                                viewChanged = True
                                rx += drot
                        elif event.key == pygame.K_d:
                                viewChanged = True
                                rx += -drot

                        elif event.key == pygame.K_r:
                                viewChanged = True
                                ry += drot
                        elif event.key == pygame.K_f:
                                viewChanged = True
                                ry += -drot

                        elif event.key == pygame.K_t:
                                viewChanged = True
                                rz += drot
                        elif event.key == pygame.K_g:
                                viewChanged = True
                                rz += -drot

        if viewChanged:
                scaleM = matrix_ops.getScaleMatrix(sc, sc, sc)
                translM = matrix_ops.getTranslationMatrix(tx, ty, tz)
                rotxM = matrix_ops.getRotateXMatrix(rx)
                rotyM = matrix_ops.getRotateYMatrix(ry)
                rotzM = matrix_ops.getRotateZMatrix(rz)

        screen.fill(BLACK)

        legend = "T: %.1f, %.1f, %.1f" % (tx, ty, tz)
        text = font.render(legend, True, (255,255,255))
        screen.blit(text, (0,0))

        legend = "S: %.1f" % (sc)
        text = font.render(legend, True, (255,255,255))
        screen.blit(text, (0,fontSize))

        oneDeg = math.pi / 180.0
        legend = "R: %.1f, %.1f, %.1f" % (rx / oneDeg, ry / oneDeg, rz / oneDeg)
        text = font.render(legend, True, (255,255,255))
        screen.blit(text, (0,fontSize * 2))

        pygame.draw.line(screen, RED, (width/2, 0), (width/2, height), 1)
        pygame.draw.line(screen, RED, (0, height/2), (width, height/2), 1)

        transformedObj = originalObj

        transformedObj = obj_file.applyTransform(transformedObj, scaleM)

        transformedObj = obj_file.applyTransform(transformedObj, rotxM)
        transformedObj = obj_file.applyTransform(transformedObj, rotyM)
        transformedObj = obj_file.applyTransform(transformedObj, rotzM)

        transformedObj = obj_file.applyTransform(transformedObj, translM)

        obj_file.drawObj(screen, o_x, o_y, transformedObj)

        pygame.display.flip()
