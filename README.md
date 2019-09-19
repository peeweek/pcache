# pCache - point cache file

`pcache` files contains simple structured data for point cache files. The file format is close to [Stanford's PLY](https://en.wikipedia.org/wiki/PLY_(file_format)) and reduces the feature set to the minimum required for storing only point data. Data types are also adjusted to be able to match the requirements of a point cache.

## Header

File header is described by a succession of ASCII Lines regardless if data is stored in binary or ASCII. Lines are ended using the **UNIX newline** character `\n`

#### Magic number

The first line of the header is always as following, in **lowercase**:

> `pcache`

#### Format identifier

The second line of the header identifies the **data format**, and the version of the data format.

`format data_format version`

Data format can be `ascii` or `binary`. Binary formats are always Little-Endian. Version information will be detailed in the Changelog.

Examples :

> `format ascii 1.0`
>
> `format binary 1.0`

#### Comments

Comments can be added with lines starting with `comment`, the end of comment is terminated by the newline.

`comment This is a really pretty comment.`

#### Element count

A line starting with `elements` will state the amount of individual elements present in the file.

`elements 9122`

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

#### Version 1.0

Initial version

