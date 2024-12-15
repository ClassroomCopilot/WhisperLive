import argparse
import ssl
import os
import socket

def check_port_availability(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('0.0.0.0', port))
    sock.close()
    return result != 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', '-p',
                        type=int,
                        default=int(os.getenv('PORT_WHISPERLIVE')),
                        help="Websocket port to run the server on.")
    parser.add_argument('--backend', '-b',
                        type=str,
                        default='faster_whisper',
                        help='Backends from ["tensorrt", "faster_whisper"]')
    parser.add_argument('--faster_whisper_custom_model_path', '-fw',
                        type=str, default=None,
                        help="Custom Faster Whisper Model")
    parser.add_argument('--trt_model_path', '-trt',
                        type=str,
                        default=None,
                        help='Whisper TensorRT model path')
    parser.add_argument('--trt_multilingual', '-m',
                        action="store_true",
                        help='Boolean only for TensorRT model. True if multilingual.')
    parser.add_argument('--ssl_cert_path', '-ssl',
                        type=str,
                        default=None,
                        help='Path to cert.pem and key.pem if ssl should be used.')
    parser.add_argument('--omp_num_threads', '-omp',
                        type=int,
                        default=1,
                        help="Number of threads to use for OpenMP")
    parser.add_argument('--no_single_model', '-nsm',
                        action='store_true',
                        help='Set this if every connection should instantiate its own model. Only relevant for custom model, passed using -trt or -fw.')
    args = parser.parse_args()

    if args.backend == "tensorrt":
        if args.trt_model_path is None:
            raise ValueError("Please Provide a valid tensorrt model path")

    port = args.port
    if not check_port_availability(port):
        print(f"Warning: Port {port} might already be in use!")
    
    ssl_context = None
    if args.ssl_cert_path is not None:
        try:
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ssl_context.load_cert_chain(
                certfile=f"{args.ssl_cert_path}/whisperlive-cert.pem",
                keyfile=f"{args.ssl_cert_path}/whisperlive-key.pem"
            )
            print("SSL context created successfully")
        except Exception as e:
            print(f"Failed to load SSL certificates: {str(e)}")
            raise

    if "OMP_NUM_THREADS" not in os.environ:
        print(f"Setting OMP_NUM_THREADS to {args.omp_num_threads}")
        os.environ["OMP_NUM_THREADS"] = str(args.omp_num_threads)

    from whisper_live.server import TranscriptionServer
    print(f"Running server with args: {args}")
    server = TranscriptionServer()
    
    print(f"Starting server on port {args.port} with backend {args.backend} using SSL: {args.ssl_cert_path is not None}")
    server.run(
        "0.0.0.0",
        port=args.port,
        backend=args.backend,
        faster_whisper_custom_model_path=args.faster_whisper_custom_model_path,
        whisper_tensorrt_path=args.trt_model_path,
        trt_multilingual=args.trt_multilingual,
        single_model=not args.no_single_model,
        ssl_context=ssl_context
    )