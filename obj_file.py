import sys, pygame, math

import matrix_ops, draw3d_ops

def create_obj_dict():
        return {
                "bezcurves": [],
                "bezpatches": [],
                "faces": [],
                "triangles": [],
                "vertices": [],
                "light": [-1000.0, 1000.0, 0.0, 1.0], # location xyz, brightness
                }

def loadFile(fname):
        ext = fname[-4:].lower()
        if ext == ".dat":
                return loadBezDatFile(fname)
        elif ext == ".obj":
                return loadObjFile(fname)

def loadBezDatFile(fname):
        with open(fname) as f:
                content = f.readlines()
        content = [x.strip() for x in content] 
        vertices = []
        bezpatches = []
        for line in content:
                if line.startswith("V"):
                        tokens = line.split()
                        x = float(tokens[1])
                        y = float(tokens[2])
                        z = float(tokens[3])
                        vertices.append((x, y, z, 1))
                elif line.startswith("P"):
                        tokens = line.split()
                        patch = []
                        for i in xrange(16):
                                vertIndex = int(tokens[1 + i])
                                patch.append(vertIndex - 1)
                        bezpatches.append(patch)
        print "--- loaded %s: %d vertices, %d bezier patches" % (fname, len(vertices), len(bezpatches))

        newVertices = []
        lastVertIndexStart = 0
        triangles = []
        for controlPoints in bezpatches:
                triVertices, bezTriangles = draw3d_ops.getBezierPatchTriangles(controlPoints, vertices)
                newVertices.extend(triVertices)
                for tri in bezTriangles:
                        newTri = (
                                tri[0] + lastVertIndexStart,
                                tri[1] + lastVertIndexStart,
                                tri[2] + lastVertIndexStart,
                                )
                        triangles.append(newTri)
                lastVertIndexStart = len(newVertices)
        print "--- transform: %d vertices, %d triangles" % (len(newVertices), len(triangles))

        objdict = create_obj_dict()
        objdict["bezpatches"] = bezpatches
        objdict["vertices"] = newVertices
        objdict["triangles"] = triangles
        return objdict

def loadObjFile(fname):
        with open(fname) as f:
                content = f.readlines()
        content = [x.strip() for x in content] 

        vertices = []
        faces = []
        triangles = []
        for line in content:
                if line.startswith("v "):
                        tokens = line.split()
                        x = float(tokens[1])
                        y = float(tokens[2])
                        z = float(tokens[3])
                        vertices.append((x, y, z, 1))
                elif line.startswith("f "):
                        faceList = []
                        tokens = line.split()[1:]
                        for faceToken in tokens:
                                faceVerts = faceToken.split("/")
                                p1 = None
                                p2 = None
                                p3 = None
                                if faceVerts[0] != "":
                                        p1 = int(faceVerts[0]) - 1
                                if faceVerts[1] != "":
                                        p2 = int(faceVerts[1]) - 1
                                if faceVerts[2] != "":
                                        p3 = int(faceVerts[2]) - 1
                                faceList.append((p1, p2, p3))

                        faces.append(faceList)

                        if len(faceList) == 3:
                                tri = (faceList[0][0], faceList[1][0], faceList[2][0])
                                triangles.append(tri)
                        else:
                                for i in xrange(1, len(faceList) - 1):
                                        tri = (faceList[0][0], faceList[i][0], faceList[i + 1][0])
                                        triangles.append(tri)

        print "--- loaded %s: %d vertices, %d faces" % (fname, len(vertices), len(faces))
        objdict = create_obj_dict()
        objdict["faces"] = faces
        objdict["triangles"] = triangles
        objdict["vertices"] = vertices
        return objdict

def applyTransform(obj, matrix):
        newVertices = []
        for vertex in obj["vertices"]:
                newVertex = matrix_ops.matrixMult(vertex, matrix)
                newVertices.append(newVertex)
        return {
                "bezcurves": obj["bezcurves"],
                "bezpatches": obj["bezpatches"],
                "faces": obj["faces"],
                "triangles": obj["triangles"],
                "vertices": newVertices,
                "light": obj["light"],
                }

def drawObj(screen, o_x, o_y, obj):
        vertices = obj["vertices"]

        # faces = obj["faces"]
        # for faceList in faces:
                # lastGeoVert = None
                # for face in faceList:
                        # currentGeoVert = vertices[face[0]]
                        # if lastGeoVert != None:
                                # draw3d_ops.drawLine(screen, o_x, o_y, lastGeoVert, currentGeoVert)
                        # lastGeoVert = currentGeoVert

        sortedTris = []
        X=0
        Y=1
        Z=2

        def getSortedTris(vertices, tris):
                def sortTris(tri):
                        a = vertices[tri[0]]
                        b = vertices[tri[1]]
                        c = vertices[tri[2]]
                        a_z = a[Z]
                        b_z = b[Z]
                        c_z = c[Z]
                        min_z = min(a_z, b_z, c_z)
                        return min_z
                return sorted(tris, key=sortTris)

        sortedTris = getSortedTris(vertices, obj["triangles"])

        for tri in sortedTris:
                draw3d_ops.drawTriangle(screen, o_x, o_y, tri, vertices, (0, 255, 128), obj["light"])

        for controlPoints in obj["bezcurves"]:
                draw3d_ops.drawBezierLine(screen, o_x, o_y, controlPoints, vertices)

        # for controlPoints in obj["bezpatches"]:
                # draw3d_ops.drawBezierPatch(screen, o_x, o_y, controlPoints, vertices)
