import os
import sys
import hou
import struct

class pcache(object):

    fileName = ""
    fileType = 'a'
    fileVersion = 1.0

    propertyNames = []
    propertyTypes = []
    propertyData = bytearray()
    itemcount = 0
    itemstride = 0
    defaultBindings = {
        'P': 'position',
        'N': 'normal',
        'v': 'velocity',
        'Cd': 'color',
        'Alpha': 'alpha',
        'uv': 'texCoord',
        'age': 'age',
        'life': 'lifetime'
    }

    components = ['x', 'y', 'z', 'w']



    def __init__(self, filename=None):
        self.clear()
        if filename is not None: # read file
            self.loadFromFile(filename)

    def clear(self):
        self.fileName = ""
        self.fileType = 'a'
        self.fileVersion = 1.0
        self.propertyNames = []
        self.propertyTypes = []
        self.propertyData = bytearray()
        self.itemcount = 0
        self.itemstride = 0

    def setDataFromGeometry(self, geo, export_attribs, property_names=None):
        # sets data into geometry
        if not isinstance(geo, hou.Geometry):
            raise hou.Error("Input is not not a valid Houdini Geometry")

        self.clear()
        bindings = {}
        attribs = export_attribs.split(' ')
        if property_names is None:  # use default corresponding table
            bindings = self.defaultBindings
        else:
            propnames = property_names.split(' ')
            for i in xrange(len(attribs)):
                bindings[attribs[i]] = propnames[i]

        retained_attribs = []
        for attrib in attribs:
            geo_attr = geo.findPointAttrib(attrib)
            if geo_attr is not None:
                data_type = geo_attr.dataType()
                if data_type == hou.attribData.Int:
                    str_type = 'int'
                elif data_type == hou.attribData.Float:
                    str_type = 'float'
                components = geo_attr.size()

                retained_attribs.append(geo_attr)
                if components == 1:  # float
                    self.propertyNames.append(bindings[attrib])
                    self.propertyTypes.append(str_type)
                    self.itemstride += 4
                elif components <= 4:  # vector
                    for i in xrange(components):
                        self.propertyNames.append(bindings[attrib] + ".{}".format(self.components[i]))
                        self.propertyTypes.append(str_type)
                        self.itemstride += 4
            else:
                raise hou.NodeWarning("Point attribute not found : {}".format(attrib))

        print("------- {} PROPERTIES --------".format(len(self.propertyNames)))
        for i in xrange(len(self.propertyNames)):
            print("Property : {} ({})".format(self.propertyNames[i], self.propertyTypes[i]))

        points = geo.points()
        numpt = len(points)
        self.itemcount = numpt

        for point in points:
            for i in xrange(len(retained_attribs)):
                attr = retained_attribs[i]
                val = point.attribValue(attr)

                if self.propertyTypes[i] == "float":
                    t = 'f'
                elif self.propertyTypes[i] == "int":
                    t = 'i'

                if attr.size() > 1:
                    for comp in val:
                        pack = struct.pack(t, comp)
                        for byte in pack:
                            self.propertyData.append(byte)
                else:
                    pack = struct.pack(t, val)
                    for byte in pack:
                        self.propertyData.append(byte)

    def __getComponentCountFromName(self, name):
        retval = 1
        for i in xrange(len(self.components)):
            if name.endswith(".{}".format(self.components[i])):
                return i+1
        return retval

    def __isVectorComponent(self, name):
        for i in xrange(len(self.components)):
            if name.endswith(".{}".format(self.components[i])):
                return True
        return False

    def __componentIndexOf(self, name):
        retval = -1
        for i in xrange(len(self.components)):
            if name.endswith(".{}".format(self.components[i])):
                return i
        return retval

    def __getNameWithoutComponent(self, name):
        retval = name
        for i in xrange(len(self.components)):
            if name.endswith(".{}".format(self.components[i])):
                return name.replace(".{}".format(self.components[i]),"")
        return retval

    def __reverseBinding(self, propertyName):
        for key in self.defaultBindings:
            if propertyName == self.defaultBindings[key]:
                return key
        return None

    def createGeo(self, geo, useRecommendedNames=True):
        # sets data into geometry
        if not isinstance(geo, hou.Geometry):
            raise hou.Error("Input is not not a valid Houdini Geometry")

        geo.clear()

        # deduce attributes to create from properties
        attribs_to_create = {}
        attribs_types_to_create = {}
        attribs_property = {}
        for i in xrange(len(self.propertyNames)):
            name = self.propertyNames[i]
            type = self.propertyTypes[i]

            comp = self.__getNameWithoutComponent(name)

            if useRecommendedNames:
                attrib_name = self.__reverseBinding(comp)
                if attrib_name is not None:
                    attribs_property[attrib_name] = comp
                    comp = attrib_name
            else:
                attribs_property[comp] = comp

            complen =  self.__getComponentCountFromName(name)
            attribs_types_to_create[comp] = type;

            if comp in attribs_to_create:
                attribs_to_create[comp] = max(attribs_to_create[comp], complen)
            else:
                attribs_to_create[comp] = complen

        # Attrib Creation, item structure
        for comp in attribs_to_create:
            if geo.findPointAttrib(comp) is None:
                print "{} point attribute not found: creating...".format(comp)
                if attribs_types_to_create[comp] == "float":
                    default_val = 0.0
                elif attribs_types_to_create[comp] == "int":
                    default_val = 0
                else:
                    default_val = None

                if attribs_to_create[comp] == 1:
                    geo.addAttrib(hou.attribType.Point, comp, default_val)
                else:
                    default_vec = list()
                    for i in xrange(attribs_to_create[comp]):
                        default_vec.append(default_val)
                    geo.addAttrib(hou.attribType.Point, comp, default_vec)

        # Data Storage
        for i in xrange(self.itemcount):
            pt = geo.createPoint()
            # get bytes
            item_data = self.propertyData[i * self.itemstride: (i * self.itemstride) + self.itemstride]
            attrib_data = {}
            # fill in data
            index = 0
            for j in xrange(len(self.propertyNames)):

                # get actual value
                if self.propertyTypes[j] == "float":
                    val = struct.unpack("f", item_data[index:index+4])
                    index += 4
                    # print "Unpack Float ({}) : {}".format(self.propertyNames[j], val[0])
                elif self.propertyTypes[j] == "int":
                    val = struct.unpack("i", item_data[index:index+4])
                    index += 4
                    # print "Unpack Integer ({}) : {}".format(self.propertyNames[j], val[0])
                else:
                    val = None

                if self.__isVectorComponent(self.propertyNames[j]):
                    # for vector stuff
                    key = self.__reverseBinding(self.__getNameWithoutComponent(self.propertyNames[j]))
                    idx = self.__componentIndexOf(self.propertyNames[j])
                    if key not in attrib_data:
                        attrib_data[key] = [0.0, 0.0, 0.0]
                    attrib_data[key][idx] = val[0]
                else:
                    # 1-component data
                    key = self.__reverseBinding(self.__getNameWithoutComponent(self.propertyNames[j]))
                    attrib_data[key] = val[0]

            # print attrib_data
            for attrib in attrib_data:
                pt.setAttribValue(attrib, attrib_data[attrib])

    def loadFromFile(self, filename):
        file = open(filename, "rb")
        with open(filename, "rb") as file:
            magic = file.readline()
            if magic != "pcache\n":
                raise hou.Error("Invalid file header: expected pcache magic number : {}".format(magic))

            self.clear()

            done = False
            while not done:
                with hou.InterruptableOperation("Loading PCACHE Header", open_interrupt_dialog=False) as operation:
                    line = file.readline().replace("\n","")
                    words = line.split(" ")
                    kw = words[0]
                    if kw == "end_header":
                        done = True
                    elif kw == "format":
                        if words[1] == "ascii":
                            self.fileType = 'a'
                        elif words[1] == "binary":
                            self.fileType = 'b'
                        else:
                            raise hou.Error("Invalid format: {}".format(words[1]))
                    elif kw == "elements":
                        count = int(words[1])
                        self.itemcount = count
                    elif kw == "property":
                        if len(words) != 3:
                            raise hou.Error("Invalid property description: {}".format(words))
                        if words[1] == "float":
                            self.propertyTypes.append("float")
                            self.propertyNames.append(words[2])
                            self.itemstride += 4
                        elif words[1] == "int":
                            self.propertyTypes.append("int")
                            self.propertyNames.append(words[2])
                            self.itemstride += 4
                    elif kw == "comment":
                        print ' '.join(words).replace("comment ", "")
            self.propertyData = bytearray(file.read())
            print "Item Stride is {} bytes".format(self.itemstride)
            length = len(self.propertyData)
            self.itemcount = length/self.itemstride
            print "Found {} bytes of data, corresponding to {} items".format(length, self.itemcount)

    def saveAsFile(self, filename):
        # save data
        file = open(filename, "wb")
        file.write("pcache\n")                                          # header magic number
        file.write("comment PCACHE file Exported from Houdini\n")       # -------------------
        file.write("format binary 1.0\n")                               # version and format
        file.write("elements {}\n".format(self.itemcount))              # item count

        for i in xrange(len(self.propertyNames)):                       # every property
            file.write("property {} {}\n".format(self.propertyTypes[i], self.propertyNames[i]))

        file.write("end_header\n")                                      # end of header
        # data
        file.write(self.propertyData)
        file.close()

