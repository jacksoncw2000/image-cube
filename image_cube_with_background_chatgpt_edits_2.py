import os
import glob
import numpy as np
from PIL import Image
import vtk
from vtkmodules.vtkCommonCore import vtkPoints
from vtkmodules.vtkFiltersSources import vtkPlaneSource

from jcw_utilities.utils_general import ensure_directory_exists

from prepare_images import prepare_images

Image.MAX_IMAGE_PIXELS = None

project_folder_name = os.getenv('PROJECT_FOLDER_NAME')

# define directories
root_directory = os.path.dirname(os.path.abspath(__file__))
source_images_directory = os.path.join(root_directory, 'source_images')
source_images_specific_project_directory = os.path.join(source_images_directory, project_folder_name)
converted_images_directory = os.path.join(root_directory, 'converted_images')
converted_files_output_directory = os.path.join(converted_images_directory, project_folder_name)

ensure_directory_exists(converted_images_directory)
ensure_directory_exists(converted_files_output_directory)

prepare_images(source_images_specific_project_directory, converted_files_output_directory)

# get the image paths
img_files = sorted(glob.glob(f'{converted_files_output_directory}/*.png'))

print(f'\n[VAR] img_files:\n{img_files}')

# load the images
img_paths = img_files[:6]  # take the first 6 images

# Load background image (replace with an image path or let it be the 7th image in the source_images project folder)
#background_image_path = "path/to/your/background_image.png"
background_image_path = img_files[6]  # assuming the 7th image as background, change as needed


def load_texture(img_path):
    img = Image.open(img_path).convert('RGB')  # explicitly convert image to RGB
    img_array = np.array(img)
    img_array = img_array[::-1]  # vtk uses a different image origin, so we flip the array

    img_array = img_array.astype(np.uint8)  # ensure the numpy array is of type uint8

    # Convert the image array to vtkImageData using vtkImageImport
    importer = vtk.vtkImageImport()
    data_string = img_array.tobytes()  # convert the array to string format
    importer.CopyImportVoidPointer(data_string, len(data_string))
    importer.SetDataScalarTypeToUnsignedChar()
    importer.SetNumberOfScalarComponents(3)
    importer.SetDataExtent(0, img_array.shape[1] - 1, 0, img_array.shape[0] - 1, 0, 0)
    importer.SetWholeExtent(0, img_array.shape[1] - 1, 0, img_array.shape[0] - 1, 0, 0)

    # create texture from the image
    texture = vtk.vtkTexture()
    texture.SetInputConnection(importer.GetOutputPort())
    texture.InterpolateOn()

    return texture


def load_background_texture(img_path):
    img = Image.open(img_path).convert('RGB')  # explicitly convert image to RGB
    img_array = np.array(img)
    img_array = img_array[::-1]  # vtk uses a different image origin, so we flip the array

    img_array = img_array.astype(np.uint8)  # ensure the numpy array is of type uint8

    # Convert the image array to vtkImageData using vtkImageImport
    importer = vtk.vtkImageImport()
    data_string = img_array.tobytes()  # convert the array to string format
    importer.CopyImportVoidPointer(data_string, len(data_string))
    importer.SetDataScalarTypeToUnsignedChar()
    importer.SetNumberOfScalarComponents(3)
    importer.SetDataExtent(0, img_array.shape[1] - 1, 0, img_array.shape[0] - 1, 0, 0)
    importer.SetWholeExtent(0, img_array.shape[1] - 1, 0, img_array.shape[0] - 1, 0, 0)

    # create texture from the image
    texture = vtk.vtkTexture()
    texture.SetInputConnection(importer.GetOutputPort())
    texture.InterpolateOn()

    return texture


# load textures
textures = [load_texture(img_path) for img_path in img_paths]

# Cube vertices and the corresponding texture coordinates
vertices = [[-1.0, -1.0, -1.0], [1.0, -1.0, -1.0], [1.0, 1.0, -1.0], [-1.0, 1.0, -1.0],
            [-1.0, -1.0, 1.0], [1.0, -1.0, 1.0], [1.0, 1.0, 1.0], [-1.0, 1.0, 1.0]]

tex_coords = [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]]

# Define the polygonal faces of the cube
faces = [[0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7], [0, 1, 2, 3], [4, 5, 6, 7]]

# Create the main renderer
renderer = vtk.vtkRenderer()

for face, texture in zip(faces, textures):
    points = vtk.vtkPoints()
    for vertex in face:
        points.InsertNextPoint(vertices[vertex])

    polygon = vtk.vtkPolygon()
    polygon.GetPointIds().SetNumberOfIds(4)
    for i in range(4):
        polygon.GetPointIds().SetId(i, i)

    polygons = vtk.vtkCellArray()
    polygons.InsertNextCell(polygon)

    polygonPolyData = vtk.vtkPolyData()
    polygonPolyData.SetPoints(points)
    polygonPolyData.SetPolys(polygons)

    texture_coords = vtk.vtkFloatArray()
    texture_coords.SetNumberOfComponents(2)
    texture_coords.SetName("Texture Coordinates")
    for tex_coord in tex_coords:
        texture_coords.InsertNextTuple(tex_coord)

    polygonPolyData.GetPointData().SetTCoords(texture_coords)

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(polygonPolyData)

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.SetTexture(texture)

    renderer.AddActor(actor)

# Create the background renderer
background_renderer = vtk.vtkRenderer()
background_renderer.SetLayer(0)
background_renderer.InteractiveOff()

# Set the background texture
background_texture = load_background_texture(background_image_path)

# Create a plane for the background
plane_source = vtkPlaneSource()
plane_source.SetOrigin(-1, -1, 0)
plane_source.SetPoint1(1, -1, 0)
plane_source.SetPoint2(-1, 1, 0)
plane_source.Update()

# Create mapper and actor for the background
background_mapper = vtk.vtkPolyDataMapper()
background_mapper.SetInputConnection(plane_source.GetOutputPort())

background_actor = vtk.vtkActor()
background_actor.SetMapper(background_mapper)
background_actor.SetTexture(background_texture)

# Add background to the background renderer
background_renderer.AddActor(background_actor)

# Create a render window and set the background renderer as the first layer
render_window = vtk.vtkRenderWindow()
render_window.SetNumberOfLayers(2)
render_window.AddRenderer(background_renderer)
render_window.AddRenderer(renderer)

# Set the main renderer as the second layer
renderer.SetLayer(1)

# create an interactor and set it to use a trackball camera
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(render_window)
interactor_style = vtk.vtkInteractorStyleTrackballCamera()
interactor.SetInteractorStyle(interactor_style)

# start the visualization
interactor.Initialize()
interactor.Start()