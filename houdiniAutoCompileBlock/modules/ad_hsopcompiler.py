"""
Houdini Auto Compile Block
Copyright 2023 Antoine Danion

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import typing, os, re
import hou

class AD_regexTools():
    """
    A bunch of methods that helps with finding matches in strings using regular expressions.
    """

    def __init__(self) -> None:
        pass

    def matchesMask(self, matches: list[re.Match]) -> tuple[int]:
        """
        return an int tuple of length len(matches[0].string)). 1 if corresponding index is in a match 0 if not.
        """

        mask: list[int] = [0 for i in range(0, len(matches[0].string))]
        for match in matches:
            for i in range(match.start(), match.end()):
                mask[i] = 1

        return tuple(mask)
    
    def invertMatchesMask(self, mask: list[int]) -> tuple[int]:
        """
        return the inverted int list. 0 = 1 and 1 = 0.
        """

        newMask = [1-i for i in mask]

        return tuple(newMask)

    def _findallMatches(self, pattern: typing.Union[str, re.Pattern], string: str, pos: int = 0, endpos: int = None) -> tuple[re.Match]:
        """
        return the tuple of all re.Match objects in "string" corresponding to "pattern".

        pos
        start of search

        endpos
        end of search
        """

        allMatches: list[re.Match] = []
        if endpos == None:
            endpos = len(string)

        if pattern.__class__ != re.Pattern:
            patternObj = re.compile(pattern)
        else:
            patternObj = pattern
        searchString = string[:]
        match = patternObj.search(searchString, pos=pos, endpos=endpos)

        while match != None:
            allMatches.append(match)
            match = patternObj.search(searchString, match.end(), endpos=endpos)

        return tuple(allMatches)
    
    def findallMatches(self, pattern: typing.Union[str, re.Pattern], string: str, mask: typing.Union[list[int], None] = None, debug=False) -> tuple[re.Match]:
        """
        return the tuple of all Match objects in "string" corresponding to "pattern".

        mask
        if an re.Match object is fully contained in a portion of "mask" where all items are equal 0, then the re.Match object is not returned.
        """

        tempAllMatches: list[re.Match] = list(self._findallMatches(pattern, string))
        allMatches = tempAllMatches[:]

        if mask != None:
            for match in tempAllMatches:
                keep = 0
                for i in range(match.start(), match.end()):
                    if i != 0:
                        keep = 1
                        break
                if keep == 0:
                    allMatches.remove(match)

        # Debug output
        if debug == True:
            print(f"{string} -> pattern = {pattern} -> {len(allMatches)} matches found :")
            for match in allMatches:
                print(match)

        return tuple(allMatches)
    
    def subMatch(self, match: re.Match, repl: str, string: str, group: int = 0, index: typing.Union[list[int], None] = None, debug=False) -> tuple[str, tuple[int]]:
        """
        return "string" where "match" is replaced by "repl".
        The portion of the string which will be replaced is equivalent to string[match.start(group):match.end(group)].

        group
        If different from 0, only the corresponding "match" subgroup will be replaced.

        index
        This method is using this list of indexes instead of directly using the indexes of items in "string".
        It can be helpful for offset the indexes, and, therefore, the match wich will be replaced.
        This argument being not ideal to use, this can be deleted in future updates.
        """

        if index == None:
            index = [i for i in range(0, len(string))]

        startReplIndex = index.index(match.start(group))
        if match.end(group) >= len(index):
            endReplIndex = len(index)
        else:
            endReplIndex = index.index(match.end(group))

        # print(string)
        # for i in index:
        #     print(i, end="")
        # print("")

        newString = string[:startReplIndex] + repl + string[endReplIndex:]
        # print(newString)
        newIndex: list[int] = index[:startReplIndex]
        newIndex.extend([index[startReplIndex] for i in range(0, len(repl))])
        newIndex.extend(index[endReplIndex:])

        # for i in newIndex:
        #     print(i, end="")
        # print("")

        # Debug output
        if debug == True:
            print(f"{match} to {repl}")
            print(newString)

        return (newString, newIndex)

    def pathEndDigits(self, path) -> typing.Union[int, None]:
        """
        return the int at the end of "path". e.g. if "path" = "/obj/geo1/null1/spare_input1" the returned value will be 1.
        return None if no digits where found.
        """
        searchResult = re.search(r"\d+$", path)

        if searchResult != None:

            return int(searchResult.group())
        
        else:
            
            return None
        
    def listToOrString(self, list: list[str]):

        string: str = ""

        for item in list:
            if item == list[-1]:
                string = string + item
            else:
                string = string + item + "|"
        
        return string

class AD_HSopCompiler():
    """
    A bunch of methods that helps with convert a sop network in order to compile it.
    """

    def __init__(self) -> None:
        self.reg = AD_regexTools()
        self.spareInputTemplate = hou.StringParmTemplate(name='spare_input', label='Spare Input ', num_components=1, string_type=hou.stringParmType.NodeReference, default_value=("",), tags={ "cook_dependent" : "1",  "opfilter" : "!!SOP!!",  "oprelative" : ".", })
        self.nodeFirstExprFunctions = (
            "arclen",
            "arclenD",
            "attriblist",
            "bbox",
            "centroid",
            "curvature",
            "degree",
            "detail",
            "detailattriblist",
            "detailattribsize",
            "detailattribtype",
            "details",
            "detailsmap",
            "detailsnummap",
            "detailvals",
            "edgegrouplist",
            "edgegroupmask",
            "groupbyval",
            "groupbyvals",
            "hasdetailattrib",
            "haspointattrib",
            "hasprimattrib",
            "hasvertexattrib",
            "isclosed",
            "iscollided",
            "isspline",
            "isstuck",
            "iswrapu",
            "iswrapv",
            "listbyval",
            "listbyvals",
            "metaweight",
            "mindist",
            "nearpoint",
            "normal",
            "npoints",
            "npointsgroup",
            "nprims",
            "nprimsgroup",
            "nuniquevals",
            "nvertices",
            "nverticesgroup",
            "point",
            "pointattriblist",
            "pointattribsize",
            "pointattribtype",
            "pointavg",
            "pointdist",
            "pointgrouplist",
            "pointgroupmask",
            "pointlist",
            "pointneighbours",
            "pointpattern",
            "points",
            "pointsmap",
            "pointsnummap",
            "pointvals",
            "prim",
            "primattriblist",
            "primattribsize",
            "primattribtype",
            "primdist",
            "primduv",
            "primgrouplist",
            "primgroupmask",
            "primlist",
            "primneighbours",
            "prims",
            "primsmap",
            "primsnummap",
            "primuv",
            "primvals",
            "realuv",
            "seampoints",
            "spknot",
            "surflen",
            "uniqueval",
            "uniquevals",
            "unituv",
            "uvdist",
            "vertex",
            "vertexattriblist",
            "vertexattribsize",
            "vertexattribtype",
            "vertexgrouplist",
            "vertexgroupmask",
            "vertexs",
            "vertexsmap",
            "vertexsnummap",
            "vertexvals",
            "volumeaverage",
            "volumegradient",
            "volumeindex",
            "volumeindextopos",
            "volumemax",
            "volumemin",
            "volumepostoindex",
            "volumeres",
            "volumesample",
            "volumevoxeldiameter"
        )
        self.nodeSecondExprFunctions = (
            "haspoint",
            "hasprim"
        )
        self.nodeThirdExprFunctions = (
            "mindist",
            "pointdist",
            "primdist"
        )
        self.nodeFourthExprFunctions = (
            "xyzdist"
        )
        self.nodeFifthExprFunctions = (
            "uvdist"
        )

    def blockEndNode(self, blockNode: hou.SopNode, debug = False) -> typing.Union[hou.SopNode, None]:
        """
        return the hou.SopNode object of type name block_end paired to "blockNode".

        blockNode
        Must be either from type name block_end or block_begin.
        """

        if blockNode.type().name() == "block_end":

            # Debug output
            if debug == True:
                print(f"{blockNode.name()} -> block_end :\n{blockNode.name()}")
                print("")

            return blockNode
        
        elif blockNode.type().name() == "block_begin":

            # Debug output
            if debug == True:
                print(f"{blockNode.name()} -> block_end :\n{hou.node(blockNode.evalParm('./blockpath'))}")
                print("")

            return hou.node(blockNode.evalParm("./blockpath"))
        
        else:

            # Debug output
            if debug == True:
                print(f"Error: {blockNode.name()} is not an instance from SOP block_end or SOP block_begin type.")
                print("")

            return None

    def pairedBlockBeginNodes(self, blockEnd: hou.SopNode, debug = False) -> typing.Union[tuple[hou.SopNode], None]:
        """
        return the list of hou.SopNode objects of type name block_begin paired to "blockEnd".

        blockEnd
        Must be from type name block_end.
        """

        blockBeginNodes: list[hou.SopNode] = []

        if blockEnd.type().name() == "block_end":

            for parm in blockEnd.parmsReferencingThis():
                node: hou.SopNode = parm.node()
                if node.type().name() == "block_begin":
                    if node.parm("./blockpath") == parm:
                        blockBeginNodes.append(node)

            # Debug output
            if debug == True:
                print(f"{blockEnd.name()} -> {len(blockBeginNodes)} paired block_begin nodes :")
                for node in blockBeginNodes:
                    print(node)
                print("")
            return tuple(blockBeginNodes)

        else:
            # Debug output
            if debug == True:
                print(f"Error: {blockEnd.name()} is not an instance from SOP block_end type.")
                print("")
            return None

    def allAncestors(self, node: hou.SopNode, stop: list[hou.SopNode] = None, debug = False) -> tuple[hou.SopNode]:
        """
        return the list of hou.SopNode objects from which "node" depends on. It includes node inputs and all references from self.referencedNodes().

        stop
        These nodes and their ancestors are not returned.
        Note that if ancestors of a node that is in "stop" are ancestors of an ancestor of "node" that is not in stop, then they are included.
        """

        ancestors: list[hou.SopNode] = []

        directInputs: list[hou.SopNode] = node.inputs()
        for directInput in directInputs:
            if directInput not in stop and directInput not in ancestors:
                ancestors.append(directInput)
        # directRefs: list[hou.SopNode] = node.references(include_children = False)
        directRefs: list[hou.SopNode] = [ref[0] for ref in self.referencedNodes(node)]
        for directRef in directRefs:
            if directRef not in stop and directRef not in ancestors:
                ancestors.append(directRef)

        for ancestor in ancestors:
            inputs: list[hou.SopNode] = ancestor.inputs()
            for input in inputs:
                if input != None and input != node:
                    if input not in stop and input not in ancestors:
                        ancestors.append(input)
            # refs: list[hou.SopNode] = ancestor.references(include_children = False)
            refs: list[hou.SopNode] = [ref[0] for ref in self.referencedNodes(ancestor)]
            if len(refs) > 0:
                for ref in refs:
                    if ref not in stop and ref != node and ref.parent() == node.parent() and ref not in ancestors:
                        ancestors.append(ref)
        
        # Debug output
        if debug == True:
            maxPrint = 50
            print(f"{node.name()} -> {len(ancestors)} ancestors :")
            for node in ancestors[:maxPrint]:
                print(node)
            if len(ancestors) > maxPrint:
                print(f"and {len(ancestors)-maxPrint} more...")
            print("")

        return tuple(ancestors)

    def allDescendants(self, node: hou.SopNode, stop: list[hou.SopNode] = None, debug = False) -> tuple[hou.SopNode]:
        """
        return the list of hou.SopNode objects which depends on "node". It includes node outputs and all dependants from hou.Node.dependents() that verify "node" in self.referencedNodes(dependant).

        stop
        These nodes and their descendants are not returned.
        Note that if descendants of a node that is in "stop" are descendants of an descendants of "node" that is not in stop, then they are included.
        """

        descendants: list[hou.SopNode] = []
        
        directOutputs: list[hou.SopNode] = node.outputs()
        for directOutput in directOutputs:
            if directOutput not in stop and directOutput not in descendants:
                descendants.append(directOutput)
        directDeps: list[hou.SopNode] = node.dependents(include_children = False)
        for directDep in directDeps:
            if directDep not in stop and directDep not in descendants:
                if node in [ref[0] for ref in self.referencedNodes(directDep)]:
                    descendants.append(directDep)

        for descendant in descendants:
            outputs: list[hou.SopNode] = descendant.outputs()
            for output in outputs:
                if output != None and output != node:
                    if output not in stop and output not in descendants:
                        descendants.append(output)
            deps: list[hou.SopNode] = descendant.dependents(include_children = False)
            if len(deps) > 0:
                for dep in deps:
                    if dep not in stop and dep != node and dep.parent() == node.parent() and dep not in descendants:
                        # print(f"{descendant} -> dep = {dep} -> {descendant in [ref[0] for ref in self.referencedNodes(dep)]}")
                        if descendant in [ref[0] for ref in self.referencedNodes(dep)]:
                            descendants.append(dep)

        # Debug output
        if debug == True:
            maxPrint = 50
            print(f"{node.name()} -> {len(descendants)} descendants :")
            for node in descendants[:maxPrint]:
                print(node)
            if len(descendants) > maxPrint:
                print(f"and {len(descendants)-maxPrint} more...")
            print("")

        return tuple(descendants)

    def allNodesInBlock(self, blockNode: hou.SopNode, debug = False) -> tuple[hou.SopNode]:
        """
        return the list of hou.SopNode objects which are in the "blockNode" corresponding block.
        """

        allNodes: list[hou.SopNode] = []

        blockEnd: hou.SopNode = self.blockEndNode(blockNode)
        blockEnd_pairedBlockBeginNodes = self.pairedBlockBeginNodes(blockEnd)[:]
        blockEnd_ancestors = self.allAncestors(blockEnd, stop=blockEnd_pairedBlockBeginNodes)[:]

        blocksBeginDescendant: list[hou.SopNode] = []
        for blockBegin in blockEnd_pairedBlockBeginNodes:
            blockBeginDescendant = self.allDescendants(blockBegin, stop=[blockEnd,])[:]
            blocksBeginDescendant.extend(blockBeginDescendant)

        allNodes.append(blockEnd)
        for ancestor in  blockEnd_ancestors:
            if ancestor in blocksBeginDescendant:
                allNodes.append(ancestor)
        allNodes.extend(blockEnd_pairedBlockBeginNodes)
        
        # Debug output
        if debug == True:
            maxPrint = 50
            print(f"{blockEnd.name()} -> {len(allNodes)} nodes in block :")
            for node in allNodes[:maxPrint]:
                print(node)
            if len(allNodes) > maxPrint:
                print(f"and {len(allNodes)-maxPrint} more...")
            print("")

        return tuple(allNodes)

    def entryPoints(self, blockNode: hou.SopNode, debug = False) -> tuple[hou.NodeConnection]:
        """
        return the list of hou.NodeConnection objects which are entries of the "blockNode" corresponding block. The output of each connection is in block and the input is outside the block.
        Note that is does not include the connections before the block_begin nodes of the corresponding block.
        """

        entryPointsConnections: list[hou.NodeConnection] = []

        blockEnd = self.blockEndNode(blockNode, debug=debug)
        blockBegins = self.pairedBlockBeginNodes(blockEnd, debug=debug)[:]
        allNodes = self.allNodesInBlock(blockNode, debug=debug)[:]

        for node in allNodes:
            if node not in blockBegins:
                for input in node.inputConnectors():
                    for connection in input:
                        if connection.inputNode() not in allNodes:
                            entryPointsConnections.append(connection)

        # Debug output
        if debug == True:
            print(f"{blockEnd.name()} -> {len(entryPointsConnections)} entry points :")
            for connection in entryPointsConnections:
                print(connection)
            print("")
        
        return tuple(entryPointsConnections)
    
    def createBlockBeginNodes(self, blockNode: hou.SopNode, debug=False) -> tuple[hou.SopNode]:
        """
        return the list of hou.SopNode objects which are created by this method.

        Creates block_begin nodes on each connection in self.entryPoints(blockNode). The nodes are paired to there corresponding block_end node.
        """

        createdNodes: list[hou.SopNode] = []

        entryPoints = self.entryPoints(blockNode, debug=debug)
        blockEnd: hou.SopNode = self.blockEndNode(blockNode)
        parent: hou.Node = blockEnd.parent()

        for connection in entryPoints:
            newBlockBegin: hou.SopNode = parent.createNode("block_begin")
            createdNodes.append(newBlockBegin)

            newBlockBegin_input: tuple[hou.SopNode, int] = (connection.inputNode(), connection.outputIndex())
            newBlockBegin_output: tuple[hou.SopNode, int] = (connection.outputNode(), connection.inputIndex())

            newBlockBegin.setInput(0, newBlockBegin_input[0], newBlockBegin_input[1])
            newBlockBegin_output[0].setInput(newBlockBegin_output[1], newBlockBegin, 0)

            newBlockBegin.parm("./method").set("input")
            newBlockBegin.parm("./blockpath").set(newBlockBegin.relativePathTo(blockEnd))

            newBlockBegin.moveToGoodPosition(move_inputs=False, move_outputs=False, move_unconnected=False)
        
        # Debug output
        if debug == True:
            print(f"{blockEnd} -> {len(createdNodes)} block_begin nodes created :")
            for node in createdNodes:
                print(node)
            print("")
        
        return tuple(createdNodes)
    
    def createCompileBlockNodes(self, blockNode: hou.SopNode, debug=False) -> tuple[hou.SopNode]:
        """
        return the list of hou.SopNode objects which are created by this method.

        Creates compile_begin nodes on each input and output connection that are at the inputs and output of "blockNode" corresponding block.
        """

        createdNodes: list[hou.SopNode] = []

        blockEnd: hou.SopNode = self.blockEndNode(blockNode)
        blocksBegin: tuple[hou.SopNode] = self.pairedBlockBeginNodes(blockEnd)
        parent: hou.SopNode = blockEnd.parent()

        inputConnections: list[hou.NodeConnection] = []
        outputConnections: list[hou.NodeConnection] = []

        for blockBegin in blocksBegin:
            for connection in blockBegin.inputConnections():
                inputConnections.append(connection)
        
        for connection in blockEnd.outputConnections():
            outputConnections.append(connection)

        newCompileEnd: hou.SopNode = parent.createNode("compile_end")
        createdNodes.append(newCompileEnd)
        newCompileEnd.setInput(0, blockEnd, 0)

        for connection in outputConnections:
            connection.outputNode().setInput(connection.inputIndex(), newCompileEnd, 0)

        newCompileEnd.moveToGoodPosition(move_inputs=False, move_outputs=False, move_unconnected=False)

        for connection in inputConnections:
            newCompileBegin: hou.SopNode = parent.createNode("compile_begin")
            createdNodes.append(newCompileBegin)

            newCompileBegin_input: tuple[hou.SopNode, int] = (connection.inputNode(), connection.outputIndex())
            newCompileBegin_output: tuple[hou.SopNode, int] = (connection.outputNode(), connection.inputIndex())

            newCompileBegin.setInput(0, newCompileBegin_input[0], newCompileBegin_input[1])
            newCompileBegin_output[0].setInput(newCompileBegin_output[1], newCompileBegin, 0)

            newCompileBegin.parm("./blockpath").set(newCompileBegin.relativePathTo(newCompileEnd))

            newCompileBegin.moveToGoodPosition(move_inputs=False, move_outputs=False, move_unconnected=False)

        # Debug output
        if debug == True:
            print(f"{blockEnd} -> {len(createdNodes)} compile nodes created :")
            for node in createdNodes:
                print(node)
            print("")

        return tuple(createdNodes)

    def existingSpareInputs(self, node: hou.SopNode, debug=False) -> tuple[hou.Parm]:
        """
        return the list of hou.Parm objects which are spare inputs in "node".
        """

        spareInputs: list[hou.Parm] = []
        spareParms: list[hou.Parm] = node.spareParms()

        for parm in spareParms:
            if re.search(r"/spare_input\d+$", parm.path()) != None:
                spareInputs.append(parm)

        # Debug output
        if debug == True:
            print(f"{node} -> {len(spareInputs)} existing spare inputs :")
            for spareInput in spareInputs:
                node = spareInput.node().node(spareInput.rawValue())
                if node != None:
                    print(f"{spareInput} referencing {node}")
                else:
                    print(f"{spareInput} referencing unknown node at {spareInput.rawValue()}")
            print("")
        
        return tuple(spareInputs)
    
    def referencedNodes(self, target: typing.Union[hou.Parm, hou.SopNode], debug=False) -> tuple[tuple[hou.SopNode, tuple[hou.Parm]]]:
        """
        return the list of hou.SopNode objects which are referenced in "target" which is either a hou.Parm object or a hou.SopNode object.
        The returned tuple is tuple[ tuple[ referencedNode, tuple[ parmsWhichReferenceIt, ] ] ]
        References are from self.referencedNodesInParm()
        """

        referencedNodes: list[list[typing.Union[hou.SopNode, list[hou.Parm]]]] = []

        if target.__class__ == hou.SopNode:
            node = target
            parms: list[hou.Parm] = node.parms()
            for parm in parms:
                # Find refs from path
                parmNodeRefs: list[hou.SopNode] = list(self.referencedNodesInParm(parm))
                # Find refs from input
                parmInputRefs: list[hou.SopNode] = []
                inputsIndexes: list[int] = list(self.referencedInputsInParm(parm))

                for index in inputsIndexes:
                    inputNode = parm.node().input(index)
                    if inputNode != None and inputNode not in parmInputRefs:
                        parmInputRefs.append(inputNode)

                parmRefs: list[hou.SopNode] = parmNodeRefs
                parmRefs.extend(parmInputRefs)                
                if len(parmRefs) > 0:
                    # Append if not in list
                    for ref in parmRefs:
                        found = 0
                        for i in referencedNodes:
                            if ref == i[0]:
                                i[1].append(parm)
                                found = 1
                                break
                        if found == 0:
                            referencedNodes.append([ref, [parm,]])
        else:
            referencedNodes.extend(self.referencedNodesInParm(target))
            referencedNodes.extend(list([target.node().input(index) for index in self.referencedInputsInParm(parm)]))
                    
        # Debug output
        if debug == True:
            print(f"{target} -> {len(referencedNodes)} existing references in embedded Hscript :")
            for ref in referencedNodes:
                print(f"{ref[0]} in :")
                for parm in ref[1]:
                    print(parm)
            print("")

        # Converting to tuple
        for i in range(0,len(referencedNodes)):
            for j in range(0,len(referencedNodes[i])):
                if j == 1:
                    referencedNodes[i][j] = tuple(referencedNodes[i][j])
            referencedNodes[i] = tuple(referencedNodes[i])
        referencedNodes = tuple(referencedNodes)

        return referencedNodes

    def referencedNodesInParm(self, parm: hou.Parm) -> tuple[hou.SopNode]:
        """
        return the list of hou.SopNode objects which are referenced in "parm".
        This takes into account keyframes.

        References are either string node paths or input references.
        e.g. : detail(0, 'attrName', 2)
                      ^
            -> 1 input reference -> 0 -> returned value will be the hou.SopNode connected in input 0
        e.g. : detail("../null1", 'attrName', 2)
                      ^
            -> 1 node reference -> "../null1" -> returned value will be the hou.SopNode self.pathToNode("../null1", parm)
        """

        refs: list[hou.SopNode] = []
        exprs: list[str] = self.exprsInParm(parm)[:]

        if len(exprs) > 0:
            for expr in exprs:

                # Finds out explicitly referenced nodes
                stringsMatches = self.matchStrings(expr)[:]
                for stringMatch in stringsMatches:
                    node = self.pathToNode(stringMatch.group().strip("\"'"), parm)
                    if node != None and node not in refs:
                        refs.append(node)
        
        if parm.parmTemplate().type() == hou.parmTemplateType.String:
            if parm.parmTemplate().stringType() == hou.stringParmType.NodeReference or parm.parmTemplate().stringType() == hou.stringParmType.NodeReferenceList:
                rawValue: str = parm.rawValue()
                splittedRawValue = rawValue.split(" ")
                for path in splittedRawValue:
                    node = self.pathToNode(path, parm)
                    if node != None and node not in refs:
                        refs.append(node)

        return tuple(refs)
    
    def exprsInParm(self, parm: hou.Parm) -> tuple[str]:
        """
        return the list of strings that are Hscript expressions in "parm".
        This takes into account keyframes.

        If an expression is in `, the expression will be returned without it.
        """

        exprs: list[str] = []

        keyframes = parm.keyframes()
        if len(keyframes) > 0:
            for key in keyframes:
                exprs.append(key.expression())
        else:
            exprs.extend([expr.group().strip("`") for expr in self.matchHscript(parm.rawValue())])

        return tuple(exprs)

    def pathToNode(self, path: str, parent: typing.Union[hou.Parm, hou.SopNode], debug=False):
        """
        return the hou.SopNode object corresponding to "path". "parent" helps to deal with relative paths.
        """

        if parent.__class__ == hou.Parm:

            try:
                node = hou.node(parent.node().node(path).path())
            except:
                node = None

        else:

            try:
                node = hou.node(parent.node(path).path())
            except:
                node = None

        return node
    
    def referencedInputsInParm(self, parm: hou.Parm) -> tuple[int]:
        """
        return the list of referenced inputs in "parm".
        e.g. : detail(0, 'attrName', 2)
                      ^
            -> 1 input reference -> returned value will be 0
        """

        refs: list[int] = []
        exprs: list[str] = self.exprsInParm(parm)[:]

        if len(exprs) > 0:
            for expr in exprs:
                inputRefsMatches = self.matchHscriptInputReferences(expr)
                for inputMatch in inputRefsMatches:
                    inputRef = int(inputMatch.group(2))
                    if inputRef not in refs:
                        refs.append(inputRef)

        return tuple(refs)

    #                                                                          parm path, Node, existing or not
    def neededSpareInputs(self, node: hou.SopNode, debug=False) -> tuple[tuple[str, hou.SopNode, bool]]:
        """
        return the list of needed spare inputs in "node".
        Returned tuple : tuple[ tuple[ spareInputPath, nodeReferencedBySpareInput, isTheSpareInputExisting ] ]
        (if isTheSpareInputExisting == False the it needs to be created)
        
        A spare input is needed in a node referencing another node. References from self.referencedNodes().
        """

        referencedNodes = self.referencedNodes(node, debug=debug)[:]

        existingSpareInputs = self.existingSpareInputs(node, debug=debug)[:]
        sortedExistingSpareInputs = sorted([spare.path() for spare in existingSpareInputs])
        sortedExistingSpareInputs = [hou.parm(path) for path in sortedExistingSpareInputs]

        if len(existingSpareInputs) > 0:
            spareInputStart = self.reg.pathEndDigits(sortedExistingSpareInputs[-1].path()) + 1
        else:
            spareInputStart = 0
        spareInputIndex = spareInputStart
        newSpareDefaultPath = node.path() + "/spare_input"

        neededSpareInputs: list[tuple[str, hou.SopNode, bool]] = []
        for ref in referencedNodes:
            found = 0
            for parm in ref[1]:
                if parm.node() == node:
                    if parm.parmTemplate().type() == hou.parmTemplateType.String:
                        if parm.parmTemplate().stringType() == hou.stringParmType.NodeReference or parm.parmTemplate().stringType() == hou.stringParmType.NodeReferenceList:
                            if len(self.exprsInParm(parm)) == 0:
                                found = 1
            for existingSpareInput in existingSpareInputs:
                if ref[0] == hou.node(existingSpareInput.rawValue()):
                    neededSpareInputs.append((existingSpareInput.path(), ref[0], True))
                    found = 1
            if found == 0 and ref[0].parent() == node.parent():
                neededSpareInputs.append((newSpareDefaultPath + str(spareInputIndex), ref[0], False))
                spareInputIndex = spareInputIndex + 1

        # Debug output
        if debug == True:
            print(f"{node} -> Starting spare input creation at {spareInputStart}")
            print(f"{node} -> {len([spare for spare in neededSpareInputs if spare[2] == False])} new spare input needed :")
            for spare in neededSpareInputs:
                if spare[2] == False:
                    print(f"{spare[0]} referencing {spare[1]}")
            print("")

        return tuple(neededSpareInputs)
    
    def createNeededSpareInputs(self, neededSpareInputs: tuple[tuple[str, hou.SopNode, bool]], debug=False):
        """
        Creates the needed spare inputs.
        """

        for spare in neededSpareInputs:
            if spare[2] == False:
                spareInputNumber: int  = self.reg.pathEndDigits(spare[0])
                node: hou.SopNode  = hou.node(os.path.dirname(spare[0]))
                referencedNode: hou.SopNode = spare[1]
                self.createSpareInput(node, spareInputNumber, referencedNode, debug=debug)
    
    def createSpareInput(self, node: hou.SopNode, spareInputNumber: int = 0, referencedNode: hou.SopNode = None, debug=False):
        """
        Creates a spare input on "node" refererencing "referencedNode".

        spareInputNumber
        The number at the end of the path of the created spare input.
        """

        newSpareInputTemplate = self.spareInputTemplate.clone()
        newSpareInputTemplate.setName(newSpareInputTemplate.name()+str(spareInputNumber))
        newSpareInputTemplate.setLabel(newSpareInputTemplate.label()+str(spareInputNumber))

        node.addSpareParmTuple(newSpareInputTemplate)
        spare = node.parm(f"./{newSpareInputTemplate.name()}")
        spare.set(node.relativePathTo(referencedNode))

        # Debug output
        if debug == True:
            print(f"{node} -> New spare input created:\n{spare} referencing {referencedNode}\n")


    def matchHscript(self, string: str) -> tuple[re.Match]:
        """
        return the list of re.Match objects that correspond to Hscript expressions in "string". ` are included.
        """
        
        HscriptPattern = r"`[^\r\n`]*`"

        allMatches: tuple[re.Match] = self.reg.findallMatches(HscriptPattern, string)
        
        return allMatches

    def matchStrings(self, expr: str) -> tuple[re.Match]:
        """
        return the list of re.Match objects that correspond to strings in "string". " and ' are included.
        """

        stringPatterns = [
            r"\"[^\r\n'\"]*\"",
            r"'[^\r\n'\"]*'"
        ]

        allStrings: list[re.Match] = []

        for pattern in stringPatterns:
            allStrings.extend(self.reg.findallMatches(pattern, expr))
        
        return tuple(allStrings)
    
    def matchHscriptInputReferences(self, expr: str, debug=False) -> tuple[re.Match]:
        """
        return the list of re.Match objects that correspond to input references in "string". " and ' are included.
        Note that there are subgroups : $1 returns the expression function
                                        $2 returns the int number referencing the input
        """

        inputReferenceFirstPattern  = f"({self.reg.listToOrString(self.nodeFirstExprFunctions)})"  r"\([ ]*(\d+)[ ]*[,\)]"
        inputReferenceSecondPattern = f"({self.reg.listToOrString(self.nodeSecondExprFunctions)})" r"\([^\r\n,]+,[ ]*(\d+)[ ]*[,\)]"
        inputReferenceThirdPattern  = f"({self.reg.listToOrString(self.nodeThirdExprFunctions)})"  r"\([^\r\n,]+,[^\r\n,]+,[ ]*(\d+)[ ]*[,\)]"
        inputReferenceFourthPattern = f"({self.reg.listToOrString(self.nodeFourthExprFunctions)})" r"\([^\r\n,]+,[^\r\n,]+,[^\r\n,]+,[ ]*(\d+)[ ]*[,\)]"
        inputReferenceFifthPattern  = f"({self.reg.listToOrString(self.nodeFifthExprFunctions)})"  r"\([^\r\n,]+,[^\r\n,]+,[^\r\n,]+,[^\r\n,]+,[ ]*(\d+)[ ]*[,\)]"
        inputReferencePatterns: tuple[str] = (
            inputReferenceFirstPattern,
            inputReferenceSecondPattern,
            inputReferenceThirdPattern,
            inputReferenceFourthPattern,
            inputReferenceFifthPattern
        )
        
        strings = self.matchStrings(expr)
        if len(strings) > 0:
            mask = self.reg.invertMatchesMask(self.reg.matchesMask(strings))
        else:
            mask = None

        allInputRefs: list[re.Match] = []
        for inputReferencesPattern in inputReferencePatterns:
            allInputRefs.extend(self.reg.findallMatches(inputReferencesPattern, expr, mask=mask))

        # Debug output
        if debug == True:
            print(f"{expr} -> {len(allInputRefs)} input references found :")
            for match in allInputRefs:
                print(f"{match} at index {match.start(2)}: {match.group(2)}")

        return tuple(allInputRefs)

    def makeExprCompilable(self, parent: typing.Union[hou.Parm, hou.SopNode], expr: str, neededSpareInputs: tuple[tuple[str, hou.SopNode, bool]], debug=False) -> str:
        """
        return the converted "expr" with spare inputs references instead of node paths and inputs references.

        parent
        The "parent" of the expression. The parm caontaining the expression or the node containing this parm.

        neededSpareInputs
        The needed spare input of the node.
        This argument may be deleted in future updates.
        """

        newExpr = expr

        # Replacing node path references
        stringsMatches = self.matchStrings(expr)
        indexMap = None
        for stringMatch in stringsMatches:
            node = self.pathToNode(stringMatch.group().strip("\"'"), parent)
            if node != None:
                spareRefNum = None
                for spare in neededSpareInputs:
                    if spare[1] == node:
                        spareRefNum = (self.reg.pathEndDigits(spare[0]) + 1)*-1
                        break
                if spareRefNum != None:
                    subMatchResult = self.reg.subMatch(stringMatch, str(spareRefNum), newExpr, index=indexMap)
                    newExpr = subMatchResult[0]
                    indexMap = subMatchResult[1]
        
        # Replacing inputs references
        inputRefMatches = self.matchHscriptInputReferences(expr, debug=debug)
        indexMap = None
        for inputRefMatch in inputRefMatches:
            inputIndex = int(inputRefMatch.group(2))
            if parent.__class__ == hou.SopNode:
                inputNode = parent.input(inputIndex)
            else:
                inputNode = parent.node().input(inputIndex)
            if inputNode != None:
                spareRefNum = None
                for spare in neededSpareInputs:
                    if spare[1] == inputNode:
                        spareRefNum = (self.reg.pathEndDigits(spare[0]) + 1)*-1
                        break
                if spareRefNum != None:
                    subMatchResult = self.reg.subMatch(inputRefMatch, str(spareRefNum), newExpr, 2, index=indexMap)
                    newExpr = subMatchResult[0]
                    indexMap = subMatchResult[1]
        
        # Debug output
        if debug == True:
            print(f"{expr} -> {len(stringsMatches)} strings found in expression :")
            for string in stringsMatches:
                print(string.group())
            print("")
        
        return newExpr

    def makeParmCompilable(self, parm: hou.Parm, neededSpareInputs: tuple[tuple[str, hou.SopNode, bool]], debug=False):
        """
        Convert parm Hscript expressions with spare inputs references instead of node paths and inputs references. (see self.makeExprCompilable())

        neededSpareInputs
        The needed spare input of the node.
        This argument may be deleted in future updates.
        """

        keyframes: list[hou.BaseKeyframe] = parm.keyframes()[:]

        if len(keyframes) > 0:

            for key in keyframes:
                rawValue: str = key.expression()
                newRawValue: str = self.makeExprCompilable(parm, rawValue, neededSpareInputs)
                key.setExpression(newRawValue)
                parm.setKeyframe(key)

                # Debug output
                if debug == True and newRawValue != rawValue:
                    if key == keyframes[0]:
                        print(f"{parm} -> Converting parm expressions :")
                    print(f"At frame : {key.frame()}")
                    print(f"from : {rawValue}")
                    print(f"to :   {newRawValue}")
                    if key == keyframes[-1]:
                        print("")
        else:

            if parm.parmTemplate().type() == hou.parmTemplateType.String:
                rawValue: str = parm.rawValue()
                newRawValue: str = rawValue

                indexMap = None
                exprs = self.matchHscript(rawValue)
                for expr in exprs:
                    newExpr = "`" + self.makeExprCompilable(parm, expr.group().strip("`"), neededSpareInputs) + "`"
                    subMatchResult = self.reg.subMatch(expr, newExpr, newRawValue, index=indexMap)
                    newRawValue = subMatchResult[0]
                    indexMap = subMatchResult[1]
                
                parm.set(newRawValue)
                
                # Debug output
                if debug == True and newRawValue != rawValue:
                    print(f"{parm} -> Converting parm expressions :")
                    print(f"from : {rawValue}")
                    print(f"to :   {newRawValue}")
                    print("")

    def makeNodeCompilable(self, node: hou.SopNode, debug=False):
        """
        Convert parm Hscript expressions with spare inputs references instead of node paths and inputs references. (see self.makeParmCompilable())
        Creates needed spare inputs. (see self.createNeededSpareInputs())
        """

        neededSpareInputs = self.neededSpareInputs(node, debug=False)
        self.createNeededSpareInputs(neededSpareInputs, debug=debug)
        
        referencedNodes = self.referencedNodes(node, debug=False)
        parms: list[hou.Parm] = []
        for referencedNode in referencedNodes:
            for parm in referencedNode[1]:
                if parm not in parms:
                    parms.append(parm)

        for parm in parms:
            self.makeParmCompilable(parm, neededSpareInputs, debug=debug)
    
    def compileBlock(self, blockNode: hou.SopNode, debug=False):
        """
        Compile the "blockNode" corresponding block.
        """

        allBlockEnd: list[hou.SopNode] = []
        for node in self.allNodesInBlock(blockNode):
            if node.type().name() == "block_end":
                allBlockEnd.append(node)

        for blockEnd in allBlockEnd:
            self.createBlockBeginNodes(blockEnd, debug=debug)
        
        self.createCompileBlockNodes(blockNode, debug=debug)

        for node in self.allNodesInBlock(blockNode):
            self.makeNodeCompilable(node, debug=debug)