import cv2 # pip install python-opencv

class QRCodeCapture():
    def __init__(self, webcam_select=0, width=1280, height=720, brightness=150) -> None:
        self.title = 'LiveLT | Version 0.1'
        self.webcam_select = webcam_select
        self.width, self.height = width, height
        self.brightness = brightness

        self.init_camera()

        self.qrscan = cv2.QRCodeDetector()
        
        self.captured_data = []

        self.capture_QRCode() # while loop

        self.capture.release()
        cv2.destroyAllWindows()
        exit(0)

    def init_camera(self):
        self.capture = cv2.VideoCapture(self.webcam_select)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.capture.set(cv2.CAP_PROP_BRIGHTNESS, self.brightness)
        self.capture.open(self.webcam_select)

    def capture_QRCode(self):
        while self.capture.isOpened():
            ret, frame = self.capture.read()

            if frame is not None:
                cv2.imshow(self.title, frame)
        
                data, points, _ = self.qrscan.detectAndDecode(frame)

                if len(data) > 0: # if a QR is detected
                    if data not in self.captured_data: # and is not a duplicate of past scan
                        self.captured_data.append(data)
                        self.return_qr_data()

                if cv2.waitKey(1) & 0xFF==27: # escape key cancel
                    break

            else:
                print('Error loading webcam. Executing re-initialization')
                self.capture.release()
                self.init_camera()

    def return_qr_data(self):
        print(self.captured_data)


QRCodeCapture(webcam_select=2)