# pCache - point cache file

**Reference Version 2.0**

`pcache` files contains simple structured data for point cache files. The file format is close to [Stanford's PLY](https://en.wikipedia.org/wiki/PLY_(file_format)) and reduces the feature set to the minimum required for storing only point data. Data types are also adjusted to be able to match the requirements of a point cache.

## Header

File header is described by a succession of ASCII statement regardless if data is stored in binary or ASCII. Statements are ended using the **UNIX newline** character `\n`

#### Magic number

The first statement of the header is always as following, in **lowercase**:

> `pcache`

#### Format identifier

The second statement of the header identifies the **data format**, and the version of the data format.

`format data_format version`

Data format can be `ascii` or `binary`. Binary formats are always Little-Endian. Version information will be detailed in the Changelog.

Examples :

> `format ascii 2.0`
>
> `format binary 2.0`

#### Comments

Comments can be added with statement starting with `comment`, the end of comment is terminated by the newline.

`comment This is a really pretty comment.`

#### Element count

A statement starting with `elements` will state the amount of individual elements present in the file, split per **frame** using spaces. 

<u>Frame count will be deduced from the length of the array of element counts in this statement.</u>

`element [count_frame1 count_frame2 count_frame3 ...]`

* For a single frame : `elements 9122`
* For multiple (4) frames : `elements 9122 7112 8933 2128`

#### Global Metadata

Global Metadata statements describe data that is **common to all points of all frames** in the point cache. Each global metadata statement is described by a type, name and its value:

* `global type name value` 

Types are described in the **Type Section** of this document, with the addition of **string** (see data section).

#### Frame Metadata

Frame Metadata statements describe data that is **common to all points of one frame** in the point cache. Each frame metadata is described by a type and a name:

*  `frame_data type name` 

Frame Metadata are stored in the Data of the point cache, prior to the frame data.

Types are described in the **Type Section** of this document.

#### Properties

Property statements describe the data layout present in the file. Every property is described in one line starting with `property` . Each property is described with a type and a name such as:

`property type name`

Types are described in the **Type Section** of this document.

#### Header Ending

Header is terminated by the end_header` statement.

## Data Structure

Data is stored into an **Array of Struct** succession of elements in both modes, starting by metadata, then all the element data.

Multiple Frame data are ordered as follows:

```[Frame1_MetaData][Frame1_ElementData][Frame2_MetaData][Frame2_ElementData]...```

#### ASCII Data

ASCII Data is stored as a succession of ASCII strings for values separated by **spaces** or **UNIX newlines** (`\n`). For readability concerns it is assumed that one element's values are separated by spaces, and elements are separated by newlines. However this convention is totally optional and not mandatory to ensure valid data. 

This means that Spaces and newlines have to be treated as the same.

<u>ASCII Data is validated using the following conventions:</u>

- Range is evaluated depending on the type
- Negative values use a leading dash (`-237`)
- Floating point values uses the dot `.` as the radix point. Floating point without fractional parts can omit the radix point and the fractional part.

#### Binary Data

Binary data is stored streamlined as a BLOB with no separators. As an array of struct.

## Geometric Coordinate System

All data stored into point cache must be stored in a **Left Hand, Y-Up** Coordinate System.

## Data Types

Common data types can be the following:

| Name     | Type                               | Stride (Bytes) |
| -------- | ---------------------------------- | -------------- |
| `char`   | 8-bit signed integer value         | 1              |
| `uchar`  | 8-bit unsigned integer value       | 1              |
| `short`  | 16-bit signed integer value        | 2              |
| `ushort` | 16-bit unsigned integer value      | 2              |
| `int`    | 32-bit signed integer value        | 4              |
| `uint`   | 32-bit unsigned integer value      | 4              |
| `float`  | 32-bit signed floating-point value | 4              |
| `double` | 64-bit signed floating-point value | 8              |

For **Global metadata** the additional types can be the following:

| Name   | Type                               | Stride (Bytes) |
| ------ | ---------------------------------- | -------------- |
| `string` | Array of ASCII Characters<br/>(With the exception of `\n`, `\r` characters) | 1              |

## Property naming and convention

<u>Metadata and Property Names are ASCII strings with the following restrictions:</u>

- name must start with an alphabetic character. [A-Z ,  a-z]
- only allowed special characters are underscore `_` and point `.`
- Dot character is assumed to reference a structured data (eg: `velocity.x`) although this is only a convention.

<u>Here is a list of naming and conventions for commonly used properties:</u>

| Name                                | Type                                | Description                                            |
| ----------------------------------- | ----------------------------------- | ------------------------------------------------------ |
| `position`                          | float, 3 components `x,y,z`         | position of the point                                  |
| `velocity`                          | float, 3 components `x,y,z`         | Velocity                                               |
| `color`                             | float/uchar, 4 components `r,g,b,a` | Color (HDR/LDR)                                        |
| `size`                              | float (multiple components) `x,y,z` | Size of the point                                      |
| `age`                               | float                               | Age of the point                                       |
| `lifetime`                          | float                               | Expected Lifetime of the point                         |
| `normal`                            | float, 3 components `x,y,z`         | Normal of the point                                    |
| `tangent`                           | float, 3 components `x,y,z`         | Tangent of the point                                   |
| `bitangent`                         | float, 3 components `x,y,z`         | Bitangent of the point                                 |
| `texcoord0`, `texcoord1`, `...`     | float (multiple components)         | Texture Coordinate of the point for specified channel. |
| `bonecount`                         | ushort                              | Number of bones in the hierarchy                       |
| `boneidx0`, `boneidx1`, `...`       | ushort                              | Index of bone used for a particular channel.           |
| `boneweight0`, `boneweight1`, `...` | float                               | Weight of bone used for a particular channel.          |

## ChangeLog

#### Version 2.0

* Added Global Metadata declaration
* Added Frame Metadata delcaration
* Changed Element count to specify element count per-frame
* Added Specification about Coordinate systems
* Added Property names and conventions
* Reinforced convention: formerly suggested, these property names become nomenclature.

#### Version 1.0

Initial version

