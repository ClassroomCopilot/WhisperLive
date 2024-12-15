import tensorflow as tf

if tf.test.is_built_with_cuda():
    print("TF is built with CUDA")
else:
    print("TF is not built with CUDA")

if tf.test.is_gpu_available(cuda_only=False, min_cuda_compute_capability=None):
    print("CUDA is available in TF")
else:
    print("CUDA is not available in TF")

if tf.test.is_built_with_cudnn():
    print("cuDNN is available")
else:
    print("cuDNN is not available")