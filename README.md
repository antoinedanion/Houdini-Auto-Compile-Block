# Houdini Auto Compile Block

Automatically compile foreach blocks in SideFX Houdini Sop context.

See [SideFX's documentation on compiled blocks](https://www.sidefx.com/docs/houdini/model/compile.html)

## Table of content

- [Houdini Auto Compile Block](#houdini-auto-compile-block)
  - [Table of content](#table-of-content)
  - [Features](#features)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Compatibility](#compatibility)
  - [Changelog](#changelog)
  - [License](#license)
  - [Notice](#notice)

## Features

- Creates *block_begin* nodes at right places on the network, pairing them to the right *block_end* node. Works for nested foreach blocks.
- Creates *compile_begin* and *compile_end* nodes at right places on the network.
- For each node in the block *(supports keyframes)* :
  - Creates the spare inputs needed by Hscript parameter expressions, and setting it to the right relative node path.
  - Replaces all node paths in Hscript parameter expressions by the corresponding spare input number.
  - Replaces all inputs references in Hscript parameter expressions by the corresponding spare input number.  
    <details>
      <summary><i>List of supported Hscript functions for input references</i></summary>

      - [arclen](https://www.sidefx.com/docs/houdini/expressions/arclen.html)
      - [arclenD](https://www.sidefx.com/docs/houdini/expressions/arclenD.html)
      - [attriblist](https://www.sidefx.com/docs/houdini/expressions/attriblist.html)
      - [bbox](https://www.sidefx.com/docs/houdini/expressions/bbox.html)
      - [centroid](https://www.sidefx.com/docs/houdini/expressions/centroid.html)
      - [curvature](https://www.sidefx.com/docs/houdini/expressions/curvature.html)
      - [degree](https://www.sidefx.com/docs/houdini/expressions/degree.html)
      - [detail](https://www.sidefx.com/docs/houdini/expressions/detail.html)
      - [detailattriblist](https://www.sidefx.com/docs/houdini/expressions/detailattriblist.html)
      - [detailattribsize](https://www.sidefx.com/docs/houdini/expressions/detailattribsize.html)
      - [detailattribtype](https://www.sidefx.com/docs/houdini/expressions/detailattribtype.html)
      - [details](https://www.sidefx.com/docs/houdini/expressions/details.html)
      - [detailsmap](https://www.sidefx.com/docs/houdini/expressions/detailsmap.html)
      - [detailsnummap](https://www.sidefx.com/docs/houdini/expressions/detailsnummap.html)
      - [detailvals](https://www.sidefx.com/docs/houdini/expressions/detailvals.html)
      - [edgegrouplist](https://www.sidefx.com/docs/houdini/expressions/edgegrouplist.html)
      - [edgegroupmask](https://www.sidefx.com/docs/houdini/expressions/edgegroupmask.html)
      - [groupbyval](https://www.sidefx.com/docs/houdini/expressions/groupbyval.html)
      - [groupbyvals](https://www.sidefx.com/docs/houdini/expressions/groupbyvals.html)
      - [hasdetailattrib](https://www.sidefx.com/docs/houdini/expressions/hasdetailattrib.html)
      - [haspoint](https://www.sidefx.com/docs/houdini/expressions/haspoint.html)
      - [haspointattrib](https://www.sidefx.com/docs/houdini/expressions/haspointattrib.html)
      - [hasprim](https://www.sidefx.com/docs/houdini/expressions/hasprim.html)
      - [hasprimattrib](https://www.sidefx.com/docs/houdini/expressions/hasprimattrib.html)
      - [hasvertexattrib](https://www.sidefx.com/docs/houdini/expressions/hasvertexattrib.html)
      - [isclosed](https://www.sidefx.com/docs/houdini/expressions/isclosed.html)
      - [iscollided](https://www.sidefx.com/docs/houdini/expressions/iscollided.html)
      - [isspline](https://www.sidefx.com/docs/houdini/expressions/isspline.html)
      - [isstuck](https://www.sidefx.com/docs/houdini/expressions/isstuck.html)
      - [iswrapu](https://www.sidefx.com/docs/houdini/expressions/iswrapu.html)
      - [iswrapv](https://www.sidefx.com/docs/houdini/expressions/iswrapv.html)
      - [listbyval](https://www.sidefx.com/docs/houdini/expressions/listbyval.html)
      - [listbyvals](https://www.sidefx.com/docs/houdini/expressions/listbyvals.html)
      - [metaweight](https://www.sidefx.com/docs/houdini/expressions/metaweight.html)
      - [mindist](https://www.sidefx.com/docs/houdini/expressions/mindist.html)
      - [nearpoint](https://www.sidefx.com/docs/houdini/expressions/nearpoint.html)
      - [normal](https://www.sidefx.com/docs/houdini/expressions/normal.html)
      - [npoints](https://www.sidefx.com/docs/houdini/expressions/npoints.html)
      - [npointsgroup](https://www.sidefx.com/docs/houdini/expressions/npointsgroup.html)
      - [nprims](https://www.sidefx.com/docs/houdini/expressions/nprims.html)
      - [nprimsgroup](https://www.sidefx.com/docs/houdini/expressions/nprimsgroup.html)
      - [nuniquevals](https://www.sidefx.com/docs/houdini/expressions/nuniquevals.html)
      - [nvertices](https://www.sidefx.com/docs/houdini/expressions/nvertices.html)
      - [nverticesgroup](https://www.sidefx.com/docs/houdini/expressions/nverticesgroup.html)
      - [point](https://www.sidefx.com/docs/houdini/expressions/point.html)
      - [pointattriblist](https://www.sidefx.com/docs/houdini/expressions/pointattriblist.html)
      - [pointattribsize](https://www.sidefx.com/docs/houdini/expressions/pointattribsize.html)
      - [pointattribtype](https://www.sidefx.com/docs/houdini/expressions/pointattribtype.html)
      - [pointavg](https://www.sidefx.com/docs/houdini/expressions/pointavg.html)
      - [pointdist](https://www.sidefx.com/docs/houdini/expressions/pointdist.html)
      - [pointgrouplist](https://www.sidefx.com/docs/houdini/expressions/pointgrouplist.html)
      - [pointgroupmask](https://www.sidefx.com/docs/houdini/expressions/pointgroupmask.html)
      - [pointlist](https://www.sidefx.com/docs/houdini/expressions/pointlist.html)
      - [pointneighbours](https://www.sidefx.com/docs/houdini/expressions/pointneighbours.html)
      - [pointpattern](https://www.sidefx.com/docs/houdini/expressions/pointpattern.html)
      - [points](https://www.sidefx.com/docs/houdini/expressions/points.html)
      - [pointsmap](https://www.sidefx.com/docs/houdini/expressions/pointsmap.html)
      - [pointsnummap](https://www.sidefx.com/docs/houdini/expressions/pointsnummap.html)
      - [pointvals](https://www.sidefx.com/docs/houdini/expressions/pointvals.html)
      - [prim](https://www.sidefx.com/docs/houdini/expressions/prim.html)
      - [primattriblist](https://www.sidefx.com/docs/houdini/expressions/primattriblist.html)
      - [primattribsize](https://www.sidefx.com/docs/houdini/expressions/primattribsize.html)
      - [primattribtype](https://www.sidefx.com/docs/houdini/expressions/primattribtype.html)
      - [primdist](https://www.sidefx.com/docs/houdini/expressions/primdist.html)
      - [primduv](https://www.sidefx.com/docs/houdini/expressions/primduv.html)
      - [primgrouplist](https://www.sidefx.com/docs/houdini/expressions/primgrouplist.html)
      - [primgroupmask](https://www.sidefx.com/docs/houdini/expressions/primgroupmask.html)
      - [primlist](https://www.sidefx.com/docs/houdini/expressions/primlist.html)
      - [primneighbours](https://www.sidefx.com/docs/houdini/expressions/primneighbours.html)
      - [prims](https://www.sidefx.com/docs/houdini/expressions/prims.html)
      - [primsmap](https://www.sidefx.com/docs/houdini/expressions/primsmap.html)
      - [primsnummap](https://www.sidefx.com/docs/houdini/expressions/primsnummap.html)
      - [primuv](https://www.sidefx.com/docs/houdini/expressions/primuv.html)
      - [primvals](https://www.sidefx.com/docs/houdini/expressions/primvals.html)
      - [realuv](https://www.sidefx.com/docs/houdini/expressions/realuv.html)
      - [seampoints](https://www.sidefx.com/docs/houdini/expressions/seampoints.html)
      - [spknot](https://www.sidefx.com/docs/houdini/expressions/spknot.html)
      - [surflen](https://www.sidefx.com/docs/houdini/expressions/surflen.html)
      - [uniqueval](https://www.sidefx.com/docs/houdini/expressions/uniqueval.html)
      - [uniquevals](https://www.sidefx.com/docs/houdini/expressions/uniquevals.html)
      - [unituv](https://www.sidefx.com/docs/houdini/expressions/unituv.html)
      - [uvdist](https://www.sidefx.com/docs/houdini/expressions/uvdist.html)
      - [vertex](https://www.sidefx.com/docs/houdini/expressions/vertex.html)
      - [vertexattriblist](https://www.sidefx.com/docs/houdini/expressions/vertexattriblist.html)
      - [vertexattribsize](https://www.sidefx.com/docs/houdini/expressions/vertexattribsize.html)
      - [vertexattribtype](https://www.sidefx.com/docs/houdini/expressions/vertexattribtype.html)
      - [vertexgrouplist](https://www.sidefx.com/docs/houdini/expressions/vertexgrouplist.html)
      - [vertexgroupmask](https://www.sidefx.com/docs/houdini/expressions/vertexgroupmask.html)
      - [vertexs](https://www.sidefx.com/docs/houdini/expressions/vertexs.html)
      - [vertexsmap](https://www.sidefx.com/docs/houdini/expressions/vertexsmap.html)
      - [vertexsnummap](https://www.sidefx.com/docs/houdini/expressions/vertexsnummap.html)
      - [vertexvals](https://www.sidefx.com/docs/houdini/expressions/vertexvals.html)
      - [volumeaverage](https://www.sidefx.com/docs/houdini/expressions/volumeaverage.html)
      - [volumegradient](https://www.sidefx.com/docs/houdini/expressions/volumegradient.html)
      - [volumeindex](https://www.sidefx.com/docs/houdini/expressions/volumeindex.html)
      - [volumeindextopos](https://www.sidefx.com/docs/houdini/expressions/volumeindextopos.html)
      - [volumemax](https://www.sidefx.com/docs/houdini/expressions/volumemax.html)
      - [volumemin](https://www.sidefx.com/docs/houdini/expressions/volumemin.html)
      - [volumepostoindex](https://www.sidefx.com/docs/houdini/expressions/volumepostoindex.html)
      - [volumeres](https://www.sidefx.com/docs/houdini/expressions/volumeres.html)
      - [volumesample](https://www.sidefx.com/docs/houdini/expressions/volumesample.html)
      - [volumevoxeldiameter](https://www.sidefx.com/docs/houdini/expressions/volumevoxeldiameter.html)
      - [xyzdist](https://www.sidefx.com/docs/houdini/expressions/xyzdist.html)
      
    </details>

**Future features**

The following features may be added in the future :
- support of variables like `$CEX`, `$CEY` and `$CEZ` for example
- non "compile-able" nodes detection
- maybe some kind of workaround for channels referencing channels using parameters expressions

> [!NOTE]
> Feel free to contact me for any feature request, or make a pull request.  
> Contact : [antoinedanion.contact@gmail.com](mailto:antoinedanion.contact@gmail.com)

## Installation

Download the last stable release of Houdini Auto Compile Block.  
Copy the `houdiniAutoCompileBlock` and `packages` folders and paste it in your `$HOUDINI_USER_PREF_DIR` directory.

> [!NOTE]
> `HOUDINI_USER_PREF_DIR`
>
> *Windows default value:*  
> `C:\Users\%username%\OneDrive\Documents\houdiniX.Y` or `C:\Users\%username%\Documents\houdiniX.Y`  
> *macOS default value:*  
> `/Users/%username%/Library/Preferences/houdini/X.Y`
> 
> See [SideFX's documentation on environment variables](https://www.sidefx.com/docs/houdini/ref/env.html)

## Usage

Right click *(RMB button)* on any Sop node. There should be a sub menu called **Auto Compile**.
You will have several options :
<dl>
  <dt>Update node</dt>
  <dd>
    It will convert your Hscript expressions referring to spare inputs instead of node paths or inputs references.
  </dd>
  <dt>Compile block</dt>
  <dd>
    It will update all nodes in block, create new block_begin nodes and new compile_begin and compile_end nodes.
  </dd>
</dl>

## Compatibility

**OS**
- Windows


**Houdini Version**
- Houdini 20.0
- Houdini 19.5

> [!NOTE]
>
> Houdini Auto Compile Block should work in Linux/macOS, however this has not been tested yet and is not officially supported.  
> 
> Houdini Auto Compile Block should work in some previous versions of Houdini, however this has not been tested yet and is not officially supported.

## Changelog

See [CHANGELOG](https://github.com/antoinedanion/Houdini-Auto-Compile-Block/blob/main/CHANGELOG.md) file

## License

See [LICENSE](https://github.com/antoinedanion/Houdini-Auto-Compile-Block/blob/main/LICENSE) file

## Notice

See [NOTICE](https://github.com/antoinedanion/Houdini-Auto-Compile-Block/blob/main/NOTICE) file