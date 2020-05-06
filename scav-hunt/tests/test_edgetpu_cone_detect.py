# Script to test the cone model detection with EDGE TPU
#
# Make sure to run this from within the scav-hunt directory

import os
import sys
sys.path.append('/home/pi/Dexter/GoPiGo3/Software/Python')
sys.path.append('..')
import scavbot
import config
from coneutils import calibrate, detect

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
# e.g. /home/pi/Desktop/code/capstone_project/capstone-project-3/scav-hunt/tests
HUNT_DIR = str.replace(TESTS_DIR, '/tests', '')
# e.g. /home/pi/Desktop/code/capstone_project/capstone-project-3/scav-hunt
MODEL_DIR = os.path.join(HUNT_DIR, 'models')
# e.g. /home/pi/Desktop/code/capstone_project/capstone-project-3/scav-hunt/models

#import pdb
#pdb.set_trace()

image_model_dir = os.path.join(MODEL_DIR, 'visual', 'custom_model_edgeTPU')
cone_model_dir = os.path.join(MODEL_DIR, 'visual', 'custom_cone_model_edgetpu')
image_dir='.'
cone_image_dir= os.path.join(image_dir, 'cones')

print('Test the loading of the TFLITE runtime and make sure the TPU is plugged in')
from tflite_runtime.interpreter import Interpreter
from tflite_runtime.interpreter import load_delegate
model_name='cone_edgetpu.tflite'
model_path = os.path.join(cone_model_dir, model_name)
interpreter = Interpreter(model_path,
  experimental_delegates=[load_delegate('libedgetpu.so.1.0')])
interpreter.allocate_tensors()
print('TFLITE and EdgeTPU successfully loaded')

from scaveye import ConeClassificationModel
model = ConeClassificationModel(
    model_dir = cone_model_dir,
    image_dir = cone_image_dir,
    graph_name='cone_detect.tflite',
    min_conf_threshold=0.3,
    use_TPU=True)

# There needs to be "cones" subdirectory in the tests folder. Within that cones subdir should be
# one directory per color cone that the model should check
assert(os.path.isdir('cones'))
colors = os.listdir('cones')

color_dict = {
    'blue':0,
    'green':1,
    'orange':2,
    'purple':3,
    'red':4,
    'yellow':5
}

results = {}
for color in colors:
    cone_images = os.listdir(os.path.join('cones', color))
    for cone_image in cone_images:
        image_path = os.path.join('cones', color, cone_image)
        cones = model.classify(image_path)
        conecolor_index = color_dict[color]
        cone_x = detect.findcone_mod(conecolor_index, cones)
        results[image_path] = cone_x

print(results)
accuracy = sum([0 if v is False else 1 for k, v in results.items()])/len(results)
print('Total Accuracy: ', "{:.2%}".format(accuracy))