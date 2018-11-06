import pygame
import math

def getProjection(o_x, o_y, x, y, z, dummy=1):
        fl = 1
        oz = 1
        divis = fl + oz + z
        if divis == 0.0:
                return None

        scale = fl / divis

        scrscale = 100
        pos = (
                o_x + x * scale * scrscale,
                o_y - y * scale * scrscale
                )
        return pos

def drawLine(screen, o_x, o_y, v1, v2, mode="simple", color=(255, 255, 255)):
        x1 = v1[0]
        y1 = v1[1]
        z1 = v1[2]

        x2 = v2[0]
        y2 = v2[1]
        z2 = v2[2]

        if mode == "simple":
                beg2d = getProjection(o_x, o_y, x1, y1, z1)
                end2d = getProjection(o_x, o_y, x2, y2, z2)
                if beg2d != None and end2d != None:
                        pygame.draw.line(screen, color, beg2d, end2d, 1)

        elif mode == "shaded":
                dx = x2-x1
                dy = y2-y1
                dz = z2-z1

                last2d = getProjection(o_x, o_y, x1, y1, z1)
                last3d = (x1, y1, z1)

                nSegments = 3
                t = 1.0 / nSegments
                dt = t
                for i in xrange(0, nSegments):
                        current3d = (
                                x1 + t * dx,
                                y1 + t * dy,
                                z1 + t * dz
                                )
                        current2d = getProjection(o_x, o_y, *current3d)

                        avg_z = (last3d[2] + current3d[2]) / 2
                        cs = abs(avg_z * 2) + 1
                        color = (0, 255 / cs, 0)
                        pygame.draw.line(screen, color, last2d, current2d, 1)

                        last2d = current2d
                        last3d = current3d
                        t += dt

def drawTriangle(screen, o_x, o_y, tri, vertices, color=(255, 255, 255), light=None):
        X=0
        Y=1
        Z=2

        a = vertices[tri[0]]
        b = vertices[tri[1]]
        c = vertices[tri[2]]

        use_color = color
        if light != None:
                ab = [
                        a[X] - b[X],
                        a[Y] - b[Y],
                        a[Z] - b[Z],
                        ]
                bc = [
                        b[X] - c[X],
                        b[Y] - c[Y],
                        b[Z] - c[Z],
                        ]
                norm = [
                        ab[Y] * bc[Z] - ab[Z] * bc[Y],
                        -(ab[X] * bc[Z] - ab[Z] * bc[X]),
                        ab[X] * bc[Y] - ab[Y] * bc[X]
                        ]
                dotProd = (
                        norm[X] * light[X]
                        + norm[Y] * light[Y]
                        + norm[Z] * light[Z]
                        )
                normMag = math.sqrt(
                        norm[X] * norm[X]
                        + norm[Y] * norm[Y]
                        + norm[Z] * norm[Z]
                        )
                lightMag = math.sqrt(
                        light[X] * light[X]
                        + light[Y] * light[Y]
                        + light[Z] * light[Z]
                        )
                if normMag == 0 or lightMag == 0:
                        lightFactor = 0
                else:
                        lightFactor = (
                                math.acos(dotProd / (normMag * lightMag)) / math.pi
                                ) * light[3]
                use_color = [
                        lightFactor * color[0],
                        lightFactor * color[1],
                        lightFactor * color[2],
                        ]

        a2d = getProjection(o_x, o_y, *a)
        b2d = getProjection(o_x, o_y, *b)
        c2d = getProjection(o_x, o_y, *c)

        pygame.draw.polygon(screen, use_color, (a2d, b2d, c2d), 0)

def getBezierInterpolation(controlPoints, vertices, t):
        ptA = vertices[controlPoints[0]]
        ptB = vertices[controlPoints[1]]
        ptC = vertices[controlPoints[2]]
        ptD = vertices[controlPoints[3]]

        nt = 1.0 - t
        nt2 = nt * nt
        t2 = t * t

        k1 = nt2 * nt
        k2 = 3 * nt2 * t
        k3 = 3 * nt * t2
        k4 = t2 * t

        ptF = (
                k1 * ptA[0] + k2 * ptB[0] + k3 * ptC[0] + k4 * ptD[0],
                k1 * ptA[1] + k2 * ptB[1] + k3 * ptC[1] + k4 * ptD[1],
                k1 * ptA[2] + k2 * ptB[2] + k3 * ptC[2] + k4 * ptD[2],
                1,
                )
        return ptF

def drawBezierLine(screen, o_x, o_y, controlPoints, vertices, color=(255, 255, 255)):
        nSteps = 10
        t = 1.0 / nSteps
        dt = t

        last2d = getProjection(o_x, o_y, *vertices[controlPoints[0]])

        for tn in xrange(0, nSteps):
                new3d = getBezierInterpolation(controlPoints, vertices, t)
                new2d = getProjection(o_x, o_y, *new3d)

                pygame.draw.line(screen, color, last2d, new2d, 1)

                last2d = new2d
                t += dt

def getBezierPatchTriangles(controlPoints, vertices, gridSize = 4):
        uCurves = [
                controlPoints[0:4],
                controlPoints[4:8],
                controlPoints[8:12],
                controlPoints[12:],
                ]

        nSteps = gridSize - 1

        grid3dPoints = []
        for iu in xrange(nSteps + 1):
                u = (1.0 / nSteps) * iu
                uVertices = [
                        getBezierInterpolation(uCurves[0], vertices, u),
                        getBezierInterpolation(uCurves[1], vertices, u),
                        getBezierInterpolation(uCurves[2], vertices, u),
                        getBezierInterpolation(uCurves[3], vertices, u),
                        ]

                vControlPoints = [0, 1, 2, 3]
                for iv in xrange(nSteps + 1):
                        v = (1.0 / nSteps) * iv
                        patchPoint = getBezierInterpolation(vControlPoints, uVertices, v)
                        grid3dPoints.append(patchPoint)

        triangles = []
        for k in xrange(gridSize - 1):
                for i in xrange(gridSize - 1):
                        start = k * gridSize
                        tri = (
                                start + i,
                                start + i + 1,
                                start + i + gridSize
                                )
                        triangles.append(tri)
                        tri = (
                                start + i + 1,
                                start + i + gridSize + 1,
                                start + i + gridSize
                                )
                        triangles.append(tri)

        return (grid3dPoints, triangles)

def drawBezierPatch(screen, o_x, o_y, controlPoints, vertices, color=(255, 255, 255), gridSize = 4):
        for vIndex in controlPoints:
                point3d = vertices[vIndex]
                point2d = getProjection(o_x, o_y, *point3d)
                point2d = [int(point2d[0]), int(point2d[1])]
                pygame.draw.circle(screen, (255, 0, 255), point2d, 1)

        return

        uCurves = [
                controlPoints[0:4],
                controlPoints[4:8],
                controlPoints[8:12],
                controlPoints[12:],
                ]

        nSteps = gridSize - 1

        grid3dPoints = []
        for iu in xrange(nSteps + 1):
                u = (1.0 / nSteps) * iu
                uVertices = [
                        getBezierInterpolation(uCurves[0], vertices, u),
                        getBezierInterpolation(uCurves[1], vertices, u),
                        getBezierInterpolation(uCurves[2], vertices, u),
                        getBezierInterpolation(uCurves[3], vertices, u),
                        ]

                vControlPoints = [0, 1, 2, 3]
                for iv in xrange(nSteps + 1):
                        v = (1.0 / nSteps) * iv
                        patchPoint = getBezierInterpolation(vControlPoints, uVertices, v)
                        grid3dPoints.append(patchPoint)

        grid2dPoints = []
        for current3d in grid3dPoints:
                current2d = getProjection(o_x, o_y, *current3d)
                grid2dPoints.append(current2d)
        # print grid2dPoints

        # horiz lines
        for i in xrange(gridSize):
                last2d = grid2dPoints[i * gridSize]
                for j in xrange(gridSize - 1):
                        new2d = grid2dPoints[i * gridSize + 1 + j]
                        pygame.draw.line(screen, color, last2d, new2d, 1)
                        last2d = new2d
        # vert lines
        for i in xrange(gridSize):
                last2d = grid2dPoints[i]
                for j in xrange(gridSize - 1):
                        new2d = grid2dPoints[i + (j + 1) * gridSize]
                        pygame.draw.line(screen, color, last2d, new2d, 1)
                        last2d = new2d

