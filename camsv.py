import cv2
from flask import Flask, render_template, Response, request
import multiprocessing
import logging
import time
import warnings

class CameraStream:
    def __init__(self, cam_id, cam_port, cam_handle):
        self.app = Flask(__name__)
        while True:
            print("Connecting to Camera...")
            try:
                self.camera = cv2.VideoCapture(cam_id)
                print(f"[done] Camera connection successful! Return: {self.camera.isOpened()}")
                break

            except:
                print("Failed to connect to camera device. Retrying in 5 seconds...")
                time.sleep(5)
        self.active_streams = {}
        self.lock = multiprocessing.Lock()
        self.host = '0.0.0.0'
        self.port = cam_port

        self.app.add_url_rule('/', 'index', self.index)
        self.app.add_url_rule('/video_feed', 'video_feed', self.video_feed)
        self.app.add_url_rule(cam_handle, 'single_image', self.single_image)

        self.process = None
        warnings.filterwarnings("ignore", category=RuntimeWarning, module="multiprocessing")

    def disable_flask_logging(self):
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)

    def run(self):
        while True:
            print("Starting Server...")
            self.process = multiprocessing.Process(target=self.app.run, kwargs={'host': self.host, 'port': self.port})
            self.process.start()
            print(f"[done] Server Started Successfully!")
            break

    def generate_frames(self, user_id):
        while True:
            if user_id not in self.active_streams:
                break

            success, frame = self.camera.read()
            if not success:
                break
            else:
                _, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

    def generate_single_image(self, user_id):
        success, frame = self.camera.read()
        if success:
            _, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

    def index(self):
        return render_template('camsv.html')

    def video_feed(self):
        user_id = request.remote_addr  # Get the user's IP address as a unique identifier

        with self.lock:
            self.active_streams[user_id] = True

        return Response(self.generate_frames(user_id), mimetype='multipart/x-mixed-replace; boundary=frame')

    def single_image(self):
        user_id = request.remote_addr  # Get the user's IP address as a unique identifier

        with self.lock:
            self.active_streams[user_id] = True

        return Response(self.generate_single_image(user_id), mimetype='multipart/x-mixed-replace; boundary=frame')

    def stop_stream(self):
        print("Stopping Stream...")
        with self.lock:
            self.active_streams.clear()
        print("Stream Stopped.")

    def stop_server(self):
        print("Stopping Server...")
        if self.process:
            self.process.terminate()
            self.process.join()
        print("Server Stopped.")