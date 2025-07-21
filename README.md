# trackshape-utils

[![GitHub release (latest by date)](https://img.shields.io/github/v/release/pgroenbaek/trackshape-utils?style=flat&label=Latest%20Version)](https://github.com/pgroenbaek/trackshape-utils/releases)
[![Python 3.6+](https://img.shields.io/badge/Python-3.6%2B-blue?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![License GNU GPL v3](https://img.shields.io/badge/License-%20%20GNU%20GPL%20v3%20-lightgrey?style=flat&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA2NDAgNTEyIj4KICA8IS0tIEZvbnQgQXdlc29tZSBGcmVlIDYuNy4yIGJ5IEBmb250YXdlc29tZSAtIGh0dHBzOi8vZm9udGF3ZXNvbWUuY29tIExpY2Vuc2UgLSBodHRwczovL2ZvbnRhd2Vzb21lLmNvbS9saWNlbnNlL2ZyZWUgQ29weXJpZ2h0IDIwMjUgRm9udGljb25zLCBJbmMuIC0tPgogIDxwYXRoIGZpbGw9IndoaXRlIiBkPSJNMzg0IDMybDEyOCAwYzE3LjcgMCAzMiAxNC4zIDMyIDMycy0xNC4zIDMyLTMyIDMyTDM5OC40IDk2Yy01LjIgMjUuOC0yMi45IDQ3LjEtNDYuNCA1Ny4zTDM1MiA0NDhsMTYwIDBjMTcuNyAwIDMyIDE0LjMgMzIgMzJzLTE0LjMgMzItMzIgMzJsLTE5MiAwLTE5MiAwYy0xNy43IDAtMzItMTQuMy0zMi0zMnMxNC4zLTMyIDMyLTMybDE2MCAwIDAtMjk0LjdjLTIzLjUtMTAuMy00MS4yLTMxLjYtNDYuNC01Ny4zTDEyOCA5NmMtMTcuNyAwLTMyLTE0LjMtMzItMzJzMTQuMy0zMiAzMi0zMmwxMjggMGMxNC42LTE5LjQgMzcuOC0zMiA2NC0zMnM0OS40IDEyLjYgNjQgMzJ6bTU1LjYgMjg4bDE0NC45IDBMNTEyIDE5NS44IDQzOS42IDMyMHpNNTEyIDQxNmMtNjIuOSAwLTExNS4yLTM0LTEyNi03OC45Yy0yLjYtMTEgMS0yMi4zIDYuNy0zMi4xbDk1LjItMTYzLjJjNS04LjYgMTQuMi0xMy44IDI0LjEtMTMuOHMxOS4xIDUuMyAyNC4xIDEzLjhsOTUuMiAxNjMuMmM1LjcgOS44IDkuMyAyMS4xIDYuNyAzMi4xQzYyNy4yIDM4MiA1NzQuOSA0MTYgNTEyIDQxNnpNMTI2LjggMTk1LjhMNTQuNCAzMjBsMTQ0LjkgMEwxMjYuOCAxOTUuOHpNLjkgMzM3LjFjLTIuNi0xMSAxLTIyLjMgNi43LTMyLjFsOTUuMi0xNjMuMmM1LTguNiAxNC4yLTEzLjggMjQuMS0xMy44czE5LjEgNS4zIDI0LjEgMTMuOGw5NS4yIDE2My4yYzUuNyA5LjggOS4zIDIxLjEgNi43IDMyLjFDMjQyIDM4MiAxODkuNyA0MTYgMTI2LjggNDE2UzExLjcgMzgyIC45IDMzNy4xeiIvPgo8L3N2Zz4=&logoColor=%23ffffff)](/LICENSE)

A collection of experimental utilities for modifying existing MSTS/ORTS shapes. Things are subject to change and may not always work as expected.

The Python module doesn’t offer much handholding, so expect things to break if you're unfamiliar with the shape format or unsure of what you're doing. Be sure to keep backups of whatever you're working on.

Although the module is named trackshape-utils, it has the capability to edit, remove, and build new geometry in any kind of MSTS/ORTS shape file - not just track shapes.

The module is named as such because it includes utility functions that make working with track shapes especially easy.

## Installation

### Install from source

```sh
git clone https://github.com/pgroenbaek/trackshape-utils.git
cd trackshape-utils
pip install --upgrade .
```

### Install from wheel

If you have downloaded a `.whl` file from the [Releases](https://github.com/pgroenbaek/trackshape-utils/releases) page, install it with:

```sh
pip install path/to/trackshape_utils‑<version>‑py3‑none‑any.whl
```

Replace `<version>` with the actual version number in the filename. For example:

```sh
pip install dist/trackshape_utils-0.4.0b0-py3-none-any.whl
```

## Usage

This is how you import the Python module in a script after it has been installed on your system.

```python
import trackshapeutils as tsu
```

To list the functions and classes available in the module:

```python
print(f"Available functions and classes:")
for item in tsu.__all__:
    if callable(getattr(tsu, item)) and not item.startswith("_"):
        print(f"- {item}")
```

### Matching shapes/files in a directory

To match shapes or files in a directory, you can use the `find_directory_files` function. It takes the directory to search, along with two lists of strings used for matches and ignores, respectively. Both lists support the use of wildcards.

The `load_shape` and `load_file` functions allow you to load shapes and other types of files, respectively. The file handle object returned by `load_file` only supports replacing text, copying, and saving the file. In contrast, the object returned by `load_shape` allows you to perform many additional operations specific to shape files.

No changes made are saved to disk until `save` is called.

```python
import trackshapeutils as tsu

shape_load_path = "./examples/data"
match_shapes = ["DB1s_*.s"]
ignore_shapes = ["*Tun*", "*Pnt*", "*Frog*"]

shape_names = tsu.find_directory_files(shape_load_path, match_shapes, ignore_shapes)
for shape_name in shape_names:
    sfile = tsu.load_shape(shape_name, shape_load_path)

    # Do stuff to the shape.

    sfile.save()

    sdfile_name = shape_name.replace(".s", ".sd")
    sdfile = tsu.load_file(sdfile_name, file_load_path)

    # Do stuff to the .sd file.

    sdfile.save()
```

### Compressing/decompressing shapes

Shape files that are loaded are typically compressed. Decompressing them requires the use of the **ffeditc\_unicode.exe** binary. This must be done before any modifications can be made. You will receive an error if you attempt to modify a compressed shape file.

The **ffeditc\_unicode.exe** binary can be found in the UTILS folder of an MSTS installation. If you do not have an MSTS CD to make an installation, you can instead use the [FFEDIT\_Sub v1.2 utility](https://www.trainsim.com/forums/filelib/search-fileid?fid=87969) by Ged Saunders to manually decompress the shape before loading it, rather than using the `decompress` function provided in this Python module.

Because the `compress` function uses the external **ffeditc\_unicode.exe** binary, you will need to use the `save` function to write any modifications to disk before compressing the shape. Otherwise, the unmodified version stored on disk will be compressed, and attempting to save changes after compression will result in an error.

```python
import trackshapeutils as tsu

ffeditc_path = "./ffeditc_unicode.exe"
shape_load_path = "./examples/data"

sfile_name = 'DB1s_a2t500r20d.s'

sfile = tsu.load_shape(sfile_name, shape_load_path)
sfile.decompress(ffeditc_path)

# Do stuff.

sfile.save()
sfile.compress(ffeditc_path)
```

### Copying shapes/files on disk

Copies can be made of both shape files and other files using the `copy` function. You must provide either a new filename, a new directory, or both.

Using the `copy` function creates a new copy of the file on disk and also returns a new file handle object for the copied file.

```python
import trackshapeutils as tsu

shape_load_path = "./examples/data"
shape_processed_path = "./examples/data/processed"

sfile_name = 'DB1s_a2t500r20d.s'
new_sfile_name = 'DB1s_a2t500r20d_copied.s'

sfile = tsu.load_shape(sfile_name, shape_load_path)
new_sfile = sfile.copy(new_filename=new_sfile_name, new_directory=shape_processed_path)

# Do stuff with the copied shape file.

new_sfile.save()
```

### Changing textures

Text can be replaced in both shape files and other types of files. This is very useful, for example, when changing textures in a shape or editing the shape name in `.sd` files.

Two functions are available for replacing text. The `replace` function performs case-sensitive matching, while `replace_ignorecase` ignores case when matching. For the latter, if a texture is defined as **DB\_Track1.ACE**, using **DB\_Track1.ace** as the match will still result in a successful match.

```python
import trackshapeutils as tsu

shape_load_path = "./examples/data"
shape_processed_path = "./examples/data/processed"

sfile_name = 'DB1s_a2t500r20d.s'
new_sfile_name = 'DB1s_a2t500r20d_modified.s'

sfile = tsu.load_shape(sfile_name, shape_load_path)
new_sfile = sfile.copy(new_filename=new_sfile_name, new_directory=shape_processed_path)

# Change textures.
new_sfile.replace_ignorecase("DB_Track1.ace", "DB_Track2.ace")
new_sfile.replace_ignorecase("DB_Track1s.ace", "DB_Track2s.ace")
new_sfile.replace_ignorecase("DB_Track1w.ace", "DB_Track2w.ace")
new_sfile.replace_ignorecase("DB_Track1sw.ace", "DB_Track2sw.ace")

new_sfile.save()
```

### Modification of vertices

Working with vertices requires that you first obtain them through the shape file handle returned by `load_shape`.

There are two ways to do this. You can use `get_vertices_in_subobject`, which requires the LOD distance level and subobject index, or you can use `get_vertices_by_prim_state`, which requires the LOD distance level and a prim state.

The exact values for the LOD distance level, subobject index, and prim state vary depending on the shape. You will need to inspect the shape file in a text editor to find the values manually.

Once you have made modifications to a vertex, you can apply the changes by using the `update_vertex` function.

```python
import trackshapeutils as tsu

shape_load_path = "./examples/data"
shape_processed_path = "./examples/data/processed"

sfile_name = 'DB1s_a2t500r20d.s'
new_sfile_name = 'DB1s_a2t500r20d_modified.s'

sfile = tsu.load_shape(sfile_name, shape_load_path)
new_sfile = sfile.copy(new_filename=new_sfile_name, new_directory=shape_processed_path)

# Set all vertex point, uv_point and normal values to 0.0 in lod_dlevel 500.
lod_dlevel = 500
subobject_idxs = new_sfile.get_subobject_idxs_in_lod_dlevel(lod_dlevel)

for subobject_idx in subobject_idxs:
    vertices_in_subobject = new_sfile.get_vertices_in_subobject(lod_dlevel, subobject_idx)

    for vertex in vertices_in_subobject:
        vertex.point.x = 0.0
        vertex.point.y = 0.0
        vertex.point.z = 0.0
        vertex.uv_point.u = 0.0
        vertex.uv_point.v = 0.0
        vertex.normal.vec_x = 0.0
        vertex.normal.vec_y = 0.0
        vertex.normal.vec_z = 0.0
        new_sfile.update_vertex(vertex)

new_sfile.save()
```

### Addition of new vertices and triangles

New vertices can be added using the `add_vertex_to_subobject` function. You are required to supply an indexed trilist to this function to associate the vertices with it.

The trilist objects can be obtained from either `get_indexed_trilists_in_subobject` or `get_indexed_trilists_in_subobject_by_prim_state`. The texture used for the new vertices is determined by the prim state index the trilist is linked to.

Triangles can be added between vertices using the `insert_triangle_between` function. This function also requires an indexed trilist, along with three vertices. All the vertices must be associated with that trilist in order to connect them with a triangle.

```python
import trackshapeutils as tsu

shape_load_path = "./examples/data"
shape_processed_path = "./examples/data/processed"

sfile_name = 'DB1s_a2t500r20d.s'
new_sfile_name = 'DB1s_a2t500r20d_modified.s'

sfile = tsu.load_shape(sfile_name, shape_load_path)
new_sfile = sfile.copy(new_filename=new_sfile_name, new_directory=shape_processed_path)

# Add three new vertices and connect them with a triangle for each prim_state named 'rail_side'
# in subobject 0 and lod_dlevel 500.
lod_dlevel = 500
subobject_idx = 0
prim_states = new_sfile.get_prim_states_by_name("rail_side")

for prim_state in prim_states:
    railside_indexed_trilists = new_sfile.get_indexed_trilists_in_subobject_by_prim_state(lod_dlevel, subobject_idx, prim_state)

    for railside_indexed_trilist in railside_indexed_trilists:
        new_point = tsu.Point(0.0, 0.0, 0.0)
        new_uv_point = tsu.UVPoint(0.0, 0.0)
        new_normal = tsu.Normal(0.0, 0.0, 0.0)
        vertex1 = new_sfile.add_vertex_to_subobject(lod_dlevel, subobject_idx, railside_indexed_trilist, new_point, new_uv_point, new_normal)
        vertex2 = new_sfile.add_vertex_to_subobject(lod_dlevel, subobject_idx, railside_indexed_trilist, new_point, new_uv_point, new_normal)
        vertex3 = new_sfile.add_vertex_to_subobject(lod_dlevel, subobject_idx, railside_indexed_trilist, new_point, new_uv_point, new_normal)
        new_sfile.insert_triangle_between(railside_indexed_trilist, vertex1, vertex2, vertex3)

new_sfile.save()
```

### Removal of triangles

Triangles can be removed in two ways. You can use the `remove_triangle_between` function to remove a specific triangle formed by three vertices. Alternatively, you can use `remove_triangles_connected_to_vertex` to remove all triangles connected to a given vertex.

Removing triangles results in the visible deletion of geometry, even though the vertices and their associated data still exist in the shape file.

```python
import trackshapeutils as tsu

shape_load_path = "./examples/data"
shape_processed_path = "./examples/data/processed"

sfile_name = 'DB1s_a2t500r20d.s'
new_sfile_name = 'DB1s_a2t500r20d_modified.s'

sfile = tsu.load_shape(sfile_name, shape_load_path)
new_sfile = sfile.copy(new_filename=new_sfile_name, new_directory=shape_processed_path)

# Get the triangle lists for each prim_state named 'rail_side' in lod_dlevel 500 and subobject_idx 0.
lod_dlevel = 500
subobject_idx = 0
prim_states = new_sfile.get_prim_states_by_name("rail_side")

for prim_state in prim_states:
    railside_indexed_trilists = new_sfile.get_indexed_trilists_in_subobject_by_prim_state(lod_dlevel, subobject_idx, prim_state)

    for railside_indexed_trilist in railside_indexed_trilists:
        # Remove the first triangle in the trilist.
        first_triangle_vertex_idxs = railside_indexed_trilist.vertex_idxs[0:3]
        vertex1 = new_sfile.get_vertex_in_subobject_by_idx(lod_dlevel, subobject_idx, first_triangle_vertex_idxs[0])
        vertex2 = new_sfile.get_vertex_in_subobject_by_idx(lod_dlevel, subobject_idx, first_triangle_vertex_idxs[1])
        vertex3 = new_sfile.get_vertex_in_subobject_by_idx(lod_dlevel, subobject_idx, first_triangle_vertex_idxs[2])
        new_sfile.remove_triangle_between(railside_indexed_trilist, vertex1, vertex2, vertex3)

        # Remove any other triangles connected to the vertices in the first triangle.
        new_sfile.remove_triangles_connected_to_vertex(railside_indexed_trilist, vertex1)
        new_sfile.remove_triangles_connected_to_vertex(railside_indexed_trilist, vertex2)
        new_sfile.remove_triangles_connected_to_vertex(railside_indexed_trilist, vertex3)

new_sfile.save()
```

### Working with trackcenters

Trackcenters make it easy to work with track shapes using the same generalized scripting logic, no matter if the track shapes are curved, straight, or have multiple parallel tracks.

The trackcenters can be loaded using the `generate_trackcenters_from_global_tsection` function, either from the global *tsection.dat* Build \#60 included with the Python module or from a file you provide. The function returns a list of trackcenters, each corresponding to a parallel track. For single-track sections, there will be only one item in the list.

You can also use `generate_trackcenters_from_local_tsection` to load data from a local *tsection.dat* file if you want to, for example, modify dynamic track section shapes generated with DynaTrax.

If needed, trackcenters can also be created manually using `generate_curve_centerpoints` and `generate_straight_centerpoints`. The functions that load from *tsection.dat* files use these internally.

The example below shows how to use `find_closest_trackcenter`, `find_closest_centerpoint`, and `signed_distance_between` to calculate the distance from a vertex to the nearest trackcenter. This is essential for generalizing your scripting logic. 

By using the distance from the center, you can easily determine which part of the track a vertex belongs to, regardless of whether the track section is curved, straight, or has multiple parallel tracks.

To calculate new vertex positions relative to the trackcenter, you can use `get_new_position_from_trackcenter` to adjust the distance from the center, and `get_new_position_along_trackcenter` to adjust the position along the trackcenter.


```python
import trackshapeutils as tsu

shape_load_path = "./examples/data"
shape_processed_path = "./examples/data/processed"

sfile_name = 'DB1s_a2t500r20d.s'
new_sfile_name = 'DB1s_a2t500r20d_modified.s'

sfile = tsu.load_shape(sfile_name, shape_load_path)
new_sfile = sfile.copy(new_filename=new_sfile_name, new_directory=shape_processed_path)

# Create trackcenter objects based on data in the global tsection.dat
# Name must match the names defined within the global tsection.dat, so replace 'DB1s_' with nothing.
tsection_sfile_name = sfile_name.replace('DB1s_', '')
trackcenters = tsu.generate_trackcenters_from_global_tsection(shape_name=tsection_sfile_name, num_points_per_meter=7)

# Get all vertices in lod_dlevel 500.
lod_dlevel = 500
subobject_idxs = new_sfile.get_subobject_idxs_in_lod_dlevel(lod_dlevel)

for subobject_idx in subobject_idxs:
    vertices_in_subobject = new_sfile.get_vertices_in_subobject(lod_dlevel, subobject_idx)

    for vertex in vertices_in_subobject:
        # Calculate distance from the closest track center to the vertex point in the xz-plane.
        closest_trackcenter = tsu.find_closest_trackcenter(vertex.point, trackcenters, plane="xz")
        closest_centerpoint = tsu.find_closest_centerpoint(vertex.point, closest_trackcenter, plane="xz")
        distance_from_center = tsu.signed_distance_between(vertex.point, closest_centerpoint, plane="xz")

        # Calculate and set a new position based on distance to the closest track center (perpendicular to the closest track center).
        new_distance_from_center = -1.4125
        new_position_from_center = tsu.get_new_position_from_trackcenter(new_distance_from_center, vertex.point, closest_trackcenter)
        vertex.point.x = new_position_from_center.x
        vertex.point.y = new_position_from_center.y
        vertex.point.z = new_position_from_center.z
        new_sfile.update_vertex(vertex)

        # Calculate and set a new position based on distance along closest track center from Point(0.0, 0.0, 0.0).
        new_distance_along_track = 10
        new_position_along_track = tsu.get_new_position_along_trackcenter(new_distance_along_track, vertex.point, closest_trackcenter)
        vertex.point.x = new_position_along_track.x
        vertex.point.y = new_position_along_track.y
        vertex.point.z = new_position_along_track.z
        new_sfile.update_vertex(vertex)

new_sfile.save()
```

## Example Scripts

### Converting DB1s to DB1fb ([script](./examples/convert_db1s_to_db1fb.py))

The DBTracks track system includes many track variants, such as with different textures, various types of sleepers, and other differences like the presence or absence of overhead wires and the German LZB cable. For some variants, such as DB1fb, not all track sections are available.

However, DB1fb sections can easily be created from DB1s sections by changing the textures and removing the LZB cable.

That is exactly what this simple script does for both curved and straight track. The script was created before the functionality to remove triangles was added, so the LZB cable is hidden by moving it below the track bed.

<!-- Image showing a shape before and after running the script: -->

<!-- ![Before and after running the script](./examples/images/convert_db1s_to_db1fb.png) -->

### Creating ATracks railheads from NR_Emb railheads ([script](./examples/change_nrembrails_to_atracksrails.py))

The old XTracks track system was created in the early 2000s and features completely square railheads. More modern track systems, such as ATracks, do not. The difference is very noticeable if you try to combine the two.

Norbert Rieger's old NR_Emb shapes with integrated railheads have railhead geometry that matches that of XTracks, making those shapes visually incompatible with ATracks.

This script adjusts the XTracks-style railheads in the NR_Emb shapes to match the geometry of ATracks. The script is fairly advanced and supports both straight and curved track sections, as well as multiple parallel tracks. Within the script, new geometry is quite literally being built and appended to the existing railheads.

<!-- Image showing a shape before and after running the script: -->

<!-- ![Before and after running the script](./examples/images/change_nrembrails_to_atracksrails.png) -->

The edited NR_Emb shapes are available for download at [trainsim.com](https://www.trainsim.com/forums/filelib/search-fileid?fid=90029).

### Copying overhead wire from one shape to another ([script](./examples/make_ohw_dblslip7_5d.py))

This is another fairly advanced script that copies the overhead wire from one of Norbert Rieger's **DblSlip7\_5d** shapes into the animated **DblSlip7\_5d** shapes created by Laci1959.

Shapes can use different internal coordinate systems. These coordinate systems are transformed into world space using the `matrix ( ... )` definitions found inside the shape files.

The script handles remapping the points and normals to align with the internal coordinate system of Laci1959's shapes. Without this step, the copied geometry would appear in the wrong position when the edited shape is rendered.

<!-- Image showing a shape before and after running the script: -->

<!-- ![Before and after running the script](./examples/images/make_ohw_dblslip7_5d.png) -->

The edited DblSlip7\_5d shapes are available for download at [the-train.de](https://the-train.de/downloads/entry/11283-dbtracks-doppelte-kreuzungsweiche-dkw-7-5/).

### Additional examples

There are further example scripts available in [this repository](https://github.com/pgroenbaek/openrails-route-dk24-objects/tree/master/Scripts/DBTracks).


## Running Tests

You can run tests manually or use `tox` to test across multiple Python versions.

### Run Tests Manually
First, install the required dependencies:

```sh
pip install pytest
```

Then, run tests with:

```sh
pytest
```


## Run Tests with `tox`

`tox` allows you to test across multiple Python environments.

### **1. Install `tox`**
```sh
pip install tox
```

### **2. Run Tests**
```sh
tox
```

This will execute tests in all specified Python versions.

### **3. `tox.ini` Configuration**
The `tox.ini` file should be in your project root:

```ini
[tox]
envlist = py36, py37, py38, py39, py310

[testenv]
deps = pytest
commands = pytest
```

Modify `envlist` to match the Python versions you want to support.

## Roadmap

There will not be any additional features added to the module in its current form.

First, a proper method for reading shapes to and from a Python data structure needs to be fully implemented. This will also significantly improve performance compared to the current implementation.

Once that is complete, new features such as adding textures and other advanced operations can be introduced, as they require changes in many parts of the shape file.

## License

This project was created by Peter Grønbæk Andersen and is licensed under [GNU GPL v3](/LICENSE).
