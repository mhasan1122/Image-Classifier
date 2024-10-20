from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from keras.models import load_model
from keras.preprocessing import image
import tensorflow as tf
from tensorflow.compat.v1 import Graph, Session  # Modify this import
import json
import os
import numpy as np

# Load label information outside the view function
with open('./models/imagenet_classes.json', 'r') as f:
    labelInfo = json.load(f)

# Load the MobileNet model outside the view function
model_graph = Graph()
with model_graph.as_default():
    tf_session = Session()
    with tf_session.as_default():
        model = load_model('./models/MobileNetModelImagenet.h5')

img_height, img_width = 224, 224


def index(request):
    context = {'a': 1}
    return render(request, 'index.html', context)


def predictImage(request):
    if request.method == 'POST' and 'filePath' in request.FILES:
        try:
            file_obj = request.FILES['filePath']

            # Use Django's FileSystemStorage to handle file storage
            fs = FileSystemStorage()
            file_path_name = fs.save(file_obj.name, file_obj)
            file_path_name = fs.url(file_path_name)
            test_image = '.' + file_path_name

            # Preprocess the image for the MobileNet model
            img = image.load_img(test_image, target_size=(img_height, img_width))
            x = image.img_to_array(img)
            x = x / 255
            x = x.reshape(1, img_height, img_width, 3)

            # Make predictions using the loaded model
            with model_graph.as_default():
                with tf_session.as_default():
                    pred = model.predict(x)

            # Get the predicted label
            predicted_label = labelInfo[str(np.argmax(pred[0]))][1]

            context = {'filePathName': file_path_name, 'predictedLabel': predicted_label}
            return render(request, 'index.html', context)

        except Exception as e:
            # Handle errors, log or display an error message to the user
            error_message = f"Error processing the image: {e}"
            context = {'error': error_message}
            return render(request, 'index.html', context)

    else:
        # Handle cases where the request method is not POST or 'filePath' is not in request.FILES
        context = {'error': 'Invalid request'}
        return render(request, 'index.html', context)


def viewDataBase(request):
    # List all images in the media directory
    media_path = './media/'
    list_of_images = os.listdir(media_path)
    list_of_images_path = [os.path.join(media_path, i) for i in list_of_images]

    context = {'listOfImagesPath': list_of_images_path}
    return render(request, 'viewDB.html', context)
