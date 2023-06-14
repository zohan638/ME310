import subprocess
import threading
import time

class Detection:
    def __init__(self, port, handle):
        self.port = port
        self.handle = handle
        self.output = 0
        self.process = None
        self.is_running = False

    def run_cpp_code(self):
        execution_command = ["./video_feed", str(self.port), str(self.handle)]
        self.process = subprocess.Popen(execution_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        self.is_running = True

        # Continuously capture the output of the C++ script
        for line in iter(self.process.stdout.readline, ''):
            self.output = line.strip()

            if not self.is_running:
                break

    def stop_cpp_code(self):
        self.is_running = False
        "Stopping C++ Script..."
        self.process.terminate()

    def get_latest_output(self):
        try:
            return int(self.output)
        except:
            return 0
    
    def run(self):
        while True:
            print("Starting detection script...")
            self.cpp_thread = threading.Thread(target=self.run_cpp_code)
            self.cpp_thread.start()
            print(f"[done] Detection Started!")
            break