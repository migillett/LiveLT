#!/usr/bin/python3

# pip install python-opencv
import cv2

class QRCodeCapture():
    def __init__(self, webcam_select=None, width=1280, height=720, brightness=150) -> None:

        self.width, self.height = width, height
        self.brightness = brightness

        self.webcam_select = webcam_select
        while self.webcam_select == None:
            self.discover_devices()

        self.init_camera()
        self.qrscan = cv2.QRCodeDetector()

        self.captured_data = []
        self.capture_QRCode() # while loop
        self.capture.release()
        cv2.destroyAllWindows()
        exit(0)

    def discover_devices(self, iterate=10): # still working on this
        # https://discuss.dizzycoding.com/listing-available-devices-in-python-opencv/
        index = 0
        print('Searching for devices...')
        while index < iterate:
            print(f'Searching device: {index}')
            cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
            if cap.read()[0]:
                print(f'Found device at index: {index}')
                # self.devices.append(index)
                self.webcam_select = index
                cap.release()
                break
            index += 1

    def init_camera(self):
        self.capture = cv2.VideoCapture(self.webcam_select, cv2.CAP_DSHOW)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.capture.set(cv2.CAP_PROP_BRIGHTNESS, self.brightness)
        self.capture.open(self.webcam_select)
        print('Webcam active')

    def capture_QRCode(self):
        while self.capture.isOpened():
            ret, frame = self.capture.read()

            if frame is not None:
                if self.webcam_view:
                    cv2.imshow('QR Code Scanner', frame)

                data, points, _ = self.qrscan.detectAndDecode(frame)

                if len(data) > 0: # if a QR is detected
                    return data
                    # if data not in self.captured_data: # and is not a duplicate of past scan
                    #     self.captured_data.append(data)

                if cv2.waitKey(1) & 0xFF==27: # escape key cancel
                    print('Webcam closed')
                    break

            else:
                print('Error loading webcam. Executing re-initialization')
                self.capture.release()
                self.init_camera()


if __name__ == "__main__":
    QRCodeCapture(webcam_select=1)
