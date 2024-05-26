# image-cube
## How to Use
### First Time Setup
1. Open the project in an integrated development environment, like Visual Studio Code.
2. In the "source_images" folder at the root of the project, create a new folder. The name does not matter; I usually name it after the project I'm working on.
3. Place 6 images in this newly created folder. These will be the images that go on the 6 sides of the cube. The files need to be either .png, .jpg, or .heic image files.
4. Create a .env file in the root directory of the project by running in Terminal:
    * On Windows: New-Item -ItemType File -Name .env
    * On Mac: touch .env
5. Copy all the text from the env_sample file into the newly created .env file.
6. In the .env file, set PROJECT_FOLDER_NAME='' to the name of the folder you created in the source_images folder. For example: PROJECT_FOLDER_NAME='project_1'
7. Make a virtual environment by running in Terminal: python -m venv venv
8. Activate the virtual environment by running in Terminal:
    * On Windows: venv/Scripts/Activate.ps1
    * On Mac: source venv/bin/activate
9. Install the required dependencies by running in Terminal: pip install -r requirements.txt
### How to Run after initial setup
 1. Run the image_cube.py file. Make sure to have a project folder set in the .env file.
## To-Do
1. See if you can add a background image to the black void.