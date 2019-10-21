# pCache - point cache file

**Reference Version 2.0**

`pcache` files contains simple structured data for point cache files. The file format is close to [Stanford's PLY](https://en.wikipedia.org/wiki/PLY_(file_format)) and reduces the feature set to the minimum required for storing only point data. Data types are also adjusted to be able to match the requirements of a point cache.

## Header

File header is described by a succession of ASCII Lines regardless if data is stored in binary or ASCII. Declarations are ended using the **UNIX newline** character `\n`

#### Magic number

The first declaration of the header is always as following, in **lowercase**:

> `pcache`

#### Format identifier

The second declaration of the header identifies the **data format**, and the version of the data format.

`format data_format version`

Data format can be `ascii` or `binary`. Binary formats are always Little-Endian. Version information will be detailed in the Changelog.

Examples :

> `format ascii 2.0`
>
> `format binary 2.0`

#### Comments

Comments can be added with declarations starting with `comment`, the end of comment is terminated by the newline.

`comment This is a really pretty comment.`

#### Frame Count

Frame Count declaration tells how many pages of data (frames) are contained in the point cache, this count will be used as count for the element count, and metadata values. 

`frames count`

For example:

* `frames 1`
* `frames 6`

This frame count declaration is optional, and omitting this declaration will interpret the frame count to 1.

This frame count must appear **prior** to any any `element`, `meta`, or `property` declaration

#### Element count

A line starting with `elements` will state the amount of individual elements present in the file, split per page data (frames) using spaces.

`element [count_frame1 count_frame2 count_frame3 ...]`

* For a single frame : `elements 9122`
* For multiple frames : `elements 9122 7112 8933 2128`

#### Metadata

Metadata describe data that is common to all points in the point cache, or common to all points in one frame of the point cache. Each metadata is described by a type, name and one or many values:

* `meta type name value`  : for a single metadata value (common to all frames)
*  `meta type name [value1 value2 value3 value4 value5 ...]` : for per-frame metadata values

Metadata value count can be only equal to **One** or the **Frame Count**

Types are described in the **Type Section** of this document.

<u>Names are ASCII strings with the following restrictions:</u>

- name must start with an alphabetic character. [A-Z ,  a-z]
- only allowed special characters are underscore `_` and point `.`
- Point is assumed to reference a structured data (eg: `velocity.x`) although this is only a convention.

#### Properties

Properties describe the data layout present in the file. Every property is described in one line starting with the `property` . Each property is described with a type and a name such as:

`property type name`

Types are described in the **Type Section** of this document.

<u>Names are ASCII strings with the following restrictions:</u>

- name must start with an alphabetic character. [A-Z ,  a-z]
- only allowed special characters are underscore `_` and point `.`
- Point is assumed to reference a structured data (eg: `velocity.x`) although this is only a convention.

#### Header Ending

Header is terminated by the line `end_header`

## Data Structure

Data is stored into an **Array of Struct** succession of elements in both modes.

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

Data types can be the following:

| Name   | Type                               | Stride (Bytes) |
| ------ | ---------------------------------- | -------------- |
| char   | 8-bit signed integer value         | 1              |
| uchar  | 8-bit unsigned integer value       | 1              |
| short  | 16-bit signed integer value        | 2              |
| ushort | 16-bit unsigned integer value      | 2              |
| int    | 32-bit signed integer value        | 4              |
| uint   | 32-bit unsigned integer value      | 4              |
| float  | 32-bit signed floating-point value | 4              |
| double | 64-bit signed floating-point value | 8              |

## Property naming and conventions

Here is a list of suggestion for common naming and conventions for commonly used properties:

| Name       | Type                                | Description                    |
| ---------- | ----------------------------------- | ------------------------------ |
| `position` | float, 3 components `x,y,z`         | position of the point          |
| `velocity` | float, 3 components `x,y,z`         | Velocity                       |
| `color`    | float/uchar, 4 components `r,g,b,a` | Color (HDR/LDR)                |
| `size`     | float (multiple components) `x,y,z` | Size of the point              |
| `age`      | float                               | Age of the point               |
| `lifetime` | float                               | Expected Lifetime of the point |



## ChangeLog

#### Version 2.0

* Added Frame Count declaration

* Added Metadata declaration
* Changed Element count to specify element count per-frame
* Added Specification about Coordinate systems

#### Version 1.0

Initial version

