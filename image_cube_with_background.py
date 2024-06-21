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

initial_update = True

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

    return texture, img.size[0], img.size[1]  # Return texture and image dimensions


def setup_initial_camera():
    main_camera = renderer.GetActiveCamera()
    main_camera.SetPosition(0, 0, 5)
    main_camera.SetFocalPoint(0, 0, 0)
    main_camera.SetViewUp(0, 1, 0)
    renderer.ResetCameraClippingRange()


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

# Load background image and get its dimensions
background_texture, bg_width, bg_height = load_background_texture(background_image_path)
bg_aspect_ratio = bg_width / bg_height

# Create the background renderer
background_renderer = vtk.vtkRenderer()
background_renderer.SetLayer(0)
background_renderer.InteractiveOff()

# Create a plane for the background
plane_source = vtkPlaneSource()

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

def update_background(obj, event):
    global initial_update
    width, height = obj.GetSize()
    
    # Check if width or height is zero
    if width == 0 or height == 0:
        # Set default size if dimensions are not valid
        width = max(width, 1)
        height = max(height, 1)
        obj.SetSize(width, height)
    
    window_aspect_ratio = width / height

    # Set up the background camera
    bg_camera = background_renderer.GetActiveCamera()
    bg_camera.ParallelProjectionOn()
    
    # Adjust the background plane size
    if window_aspect_ratio > bg_aspect_ratio:
        # Window is wider than the image
        plane_height = 2.0
        plane_width = plane_height * window_aspect_ratio
    else:
        # Window is taller than the image
        plane_width = 2.0
        plane_height = plane_width / window_aspect_ratio

    plane_source.SetOrigin(-plane_width/2, -plane_height/2, 0)
    plane_source.SetPoint1(plane_width/2, -plane_height/2, 0)
    plane_source.SetPoint2(-plane_width/2, plane_height/2, 0)
    plane_source.Update()

    # Set the camera to view the entire background plane
    bg_camera.SetParallelScale(plane_height / 2)
    bg_camera.SetPosition(0, 0, 1)  # Set camera in front of the plane
    bg_camera.SetFocalPoint(0, 0, 0)  # Look at the center of the plane
    bg_camera.SetViewUp(0, 1, 0)

    # Only set up the main camera on the first update
    if initial_update:
        setup_initial_camera()
        initial_update = False

    background_renderer.ResetCameraClippingRange()


# Set up the window resize callback
render_window.AddObserver("ModifiedEvent", update_background)

setup_initial_camera()

# Create an interactor and set it to use a trackball camera
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(render_window)
interactor_style = vtk.vtkInteractorStyleTrackballCamera()
interactor.SetInteractorStyle(interactor_style)

# Set initial window size
render_window.SetSize(800, 600)  # You can adjust these values as needed

render_window.AddObserver("ModifiedEvent", update_background)

# Ensure the background renderer fills the entire viewport
background_renderer.SetViewport(0, 0, 1, 1)

# Start the visualization
interactor.Initialize()
interactor.Start()