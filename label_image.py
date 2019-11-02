# Copyright 2017 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import tensorflow as tf


class LabelImage:
    def __init__(self,
                 filename="tensorflow/examples/label_image/data/grace_hopper.jpg",
                 model_file="tensorflow/examples/label_image/data/inception_v3_2016_08_28_frozen.pb",
                 label_file="tensorflow/examples/label_image/data/imagenet_slim_labels.txt",
                 input_height=299, input_width=299, input_mean=0, input_std=255,
                 input_layer="input", output_layer="InceptionV3/Predictions/Reshape_1"):

        self.filename = filename
        self.model_file = model_file
        self.label_file = label_file
        self.input_height = input_height
        self.input_width = input_width
        self.input_mean = input_mean
        self.input_std = input_std
        self.input_layer = input_layer
        self.output_layer = output_layer

    def load_labels(self):
        label = []
        proto_as_ascii_lines = tf.io.gfile.GFile(self.label_file).readlines()
        for l in proto_as_ascii_lines:
            label.append(l.rstrip())
        return label

    def read_tensor_from_image_file(self):
        file_reader = tf.io.read_file(self.filename, "file_reader")
        if self.filename.endswith(".png"):
            image_reader = tf.image.decode_png(
                file_reader, channels=3, name="png_reader")
        elif self.filename.endswith(".gif"):
            image_reader = tf.squeeze(
                tf.image.decode_gif(file_reader, name="gif_reader"))
        elif self.filename.endswith(".bmp"):
            image_reader = tf.image.decode_bmp(file_reader, name="bmp_reader")
        else:
            image_reader = tf.image.decode_jpeg(file_reader, channels=3, name="jpeg_reader")
        float_caster = tf.cast(image_reader, tf.float32)
        dims_expander = tf.expand_dims(float_caster, 0)
        resized = tf.compat.v1.image.resize_bilinear(dims_expander, [self.input_height, self.input_width])
        normalized = tf.divide(tf.subtract(resized, [self.input_mean]), [self.input_std])
        sess = tf.compat.v1.Session()
        result = sess.run(normalized)

        return result

    def load_graph(self):
        graph = tf.Graph()
        graph_def = tf.compat.v1.GraphDef()

        with open(self.model_file, "rb") as f:
            graph_def.ParseFromString(f.read())
        with graph.as_default():
            tf.import_graph_def(graph_def)

        return graph

    def run(self):
        graph = self.load_graph()
        t = self.read_tensor_from_image_file()

        input_operation = graph.get_operation_by_name(f"import/{self.input_layer}")
        output_operation = graph.get_operation_by_name(f"import/{self.output_layer}")

        with tf.compat.v1.Session(graph=graph) as sess:
            results = sess.run(output_operation.outputs[0], {
                input_operation.outputs[0]: t
            })
        results = np.squeeze(results)
        labels = self.load_labels()

        return labels[0], results[0]
