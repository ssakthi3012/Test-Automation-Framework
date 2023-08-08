from ppadb.client import Client as AdbClient
import pytesseract
import cv2
import numpy as np
import time

from TAF import taftrace as logger
import logging
import os
import sys
import xlrd
import openpyxl
from autologging import logged, TRACE, traced
from robot.libraries.BuiltIn import BuiltIn
from robot.api import ContinuableFailure
from robot.result import Keyword as KeywordResult
from robot.running import Keyword
from robot.running.statusreporter import StatusReporter
import base64


class ADBController:

    def __init__(self, host="127.0.0.1", port=5037, device_host="192.168.1.3", device_port=5555):
            self.client = AdbClient(host=host, port=port)
            self.client.remote_connect(device_host, device_port)
            self.device = self.client.device(f"{device_host}:{device_port}")

    # def image_to_base64(self, image_path):
    #         with open(image_path, "rb") as image_file:
    #             base64_image = base64.b64encode(image_file.read()).decode("utf-8")
    #         return base64_image

    def image_to_base64(self, image_path):
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")
            self.logger.log_message(f"image to base64")
        return base64_image


    def delay(self, wait_time=1.0):
      self.logger.log_message(f"Delaying for {wait_time} seconds")
      time.sleep(float(wait_time))
      self.logger.log_message("Delay completed")
      #self.logger.log.info(f"delay time is {wait_time}")

    def take_screenshot(self, filename):
        home = self.device.screencap()
        with open(filename, "wb") as fp:
            fp.write(home)
        #self.logger.log.info(f"Screenshot saved as {filename}")

    def tap(self,x,y):
        tap_1 = self.device.input_tap(x, y)#200,240
        return tap_1
        #self.logger.log.info(f" selected input_tap is {(x, y)}")

    def radio_screen(self):
        tap_2 = self.device.input_tap(200, 240)
        return tap_2

    def keyenvents(self, keyeventvalue):
        check = self.device.input_keyevent(keyeventvalue)
        return check

    def swipe(self):
        check = self.device.input_swipe(799, 240, 250, 240, 500)
        return check

    def verifyimage(self, originalimage, referenceimage, savedimage):
        complete_image = cv2.imread(originalimage)
        crop_image = cv2.imread(referenceimage)

        crop_image_gray = cv2.cvtColor(crop_image, cv2.COLOR_BGR2GRAY)
        complete_image_gray = cv2.cvtColor(complete_image, cv2.COLOR_BGR2GRAY)

        result = cv2.matchTemplate(complete_image_gray, crop_image_gray, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        threshold = 0.8

        if max_val >= threshold:
            print("Setting Icon found in the Home page.")

            crop_width, crop_height = crop_image.shape[1], crop_image.shape[0]

            top_left = max_loc
            bottom_right = (top_left[0] + crop_width, top_left[1] + crop_height)

            marked_image = complete_image.copy()
            cv2.rectangle(marked_image, top_left, bottom_right, (0, 255, 0), 2)

            cv2.imwrite(savedimage, marked_image)

            print("Marked image saved as 'verified_setting_icon.png'.")
        else:
            print("Setting Icon not found in the complete image.")

    # def button_on_off(self, testimage, ref_on_image, ref_off_image, reference_image):
    #     complete_image = cv2.imread(testimage)
    #     touch_sound_on = cv2.imread(ref_on_image)
    #     touch_sound_off = cv2.imread(ref_off_image)
    #
    #     complete_image_gray = cv2.cvtColor(complete_image, cv2.COLOR_BGR2GRAY)
    #     #cv2.imshow(complete_image_gray)
    #     touch_sound_on_gray = cv2.cvtColor(touch_sound_on, cv2.COLOR_BGR2GRAY)
    #     touch_sound_off_gray = cv2.cvtColor(touch_sound_off, cv2.COLOR_BGR2GRAY)
    #
    #     result_on = cv2.matchTemplate(complete_image_gray, touch_sound_on_gray, cv2.TM_CCOEFF_NORMED)
    #     _, max_val_on, _, max_loc_on = cv2.minMaxLoc(result_on)
    #
    #     result_off = cv2.matchTemplate(complete_image_gray, touch_sound_off_gray, cv2.TM_CCOEFF_NORMED)
    #     _, max_val_off, _, max_loc_off = cv2.minMaxLoc(result_off)
    #
    #     threshold = 0.8
    #
    #     if max_val_on >= threshold:
    #         print("Touch sound option is present in the complete image.")
    #         if max_val_on > max_val_off:
    #             print("Touch sound is ON.")
    #             top_left = max_loc_on
    #             bottom_right = (top_left[0] + touch_sound_on_gray.shape[1], top_left[1] + touch_sound_on_gray.shape[0])
    #             cv2.rectangle(complete_image, top_left, bottom_right, (255, 0, 0), 2)
    #             region = complete_image[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
    #             mean_color = np.mean(region)
    #
    #             print(mean_color)
    #             if mean_color > 100:  # Adjust threshold for blue color detection
    #                 pass
    #             # else:
    #             #    pass
    #         else:
    #             print("Touch sound is OFF.")
    #             if max_val_off >= threshold:
    #                 top_left = max_loc_off
    #                 bottom_right = (
    #                     top_left[0] + touch_sound_off_gray.shape[1], top_left[1] + touch_sound_off_gray.shape[0])
    #                 cv2.rectangle(complete_image, top_left, bottom_right, (128, 128, 128), 2)
    #                 region = complete_image[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
    #                 mean_color = np.mean(region)
    #                 print("IFF:", mean_color)
    #                 print("off:", mean_color)
    #                 if mean_color < 150:  # Adjust threshold for gray color detection
    #                    pass
    #                 # else:
    #                 #    pass
    #             else:
    #                 print("Touch sound OFF condition not detected.")
    #
    #         cv2.imwrite(reference_image, complete_image)
    #         print("Marked image saved as 'marked_image.png'.")
    #     else:
    #         print("Touch sound option is not found in the complete image.")

    def button_on_off(self, testimage, ref_image):
        complete_image = cv2.imread(testimage)
        ref_image = cv2.imread(ref_image)

        complete_image_gray = cv2.cvtColor(complete_image, cv2.COLOR_BGR2GRAY)
        ref_image_gray = cv2.cvtColor(ref_image, cv2.COLOR_BGR2GRAY)

        result = cv2.matchTemplate(complete_image_gray, ref_image_gray, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(result)

        threshold = 0.8

        if max_val <= threshold:
            print("Touch sound is enabled.")
            # Perform additional actions or validations for Touch sound enabled
            print("Pass: Touch sound enabled")
        else:
            print("Touch sound is disabled.")
            # Perform additional actions or validations for Touch sound disabled
            print("Fail: Touch sound disabled")

    def findtext(self, image, text):
        image = cv2.imread(image)
        self.logger.log_message("Starting extracted_text")
        extracted_text = pytesseract.image_to_string(image)
        self.logger.log_message("Completeing extracted_text")

        if text in extracted_text:
            print(f"The word '{text}' is present in the image.")
            self.logger.log_message(f"The word '{text}' is present in the image.")

        else:
            print(f"The word '{text}' is not found in the image.")
            raise AssertionError(f"The word '{text}' is not found in the image.")


#
    # def button_on_off(testimage, ref_on_image, ref_off_image):
    #     complete_image = cv2.imread(testimage)
    #     ref_image_1 = cv2.imread(ref_on_image)
    #     ref_image_2 = cv2.imread(ref_off_image)
    #     complete_image_gray = cv2.cvtColor(complete_image, cv2.COLOR_BGR2GRAY)
    #     ref_image_1_gray = cv2.cvtColor(ref_image_1, cv2.COLOR_BGR2GRAY)
    #     ref_image_2_gray = cv2.cvtColor(ref_image_2, cv2.COLOR_BGR2GRAY)
    #     result_on = cv2.matchTemplate(complete_image_gray, ref_image_1_gray, cv2.TM_CCOEFF_NORMED)
    #     _, max_val_on, _, max_loc_on = cv2.minMaxLoc(result_on)
    #     result_off = cv2.matchTemplate(complete_image_gray, ref_image_2_gray, cv2.TM_CCOEFF_NORMED)
    #     _, max_val_off, _, max_loc_off = cv2.minMaxLoc(result_off)
    #     threshold = 0.8
    #     if max_val_on >= threshold:
    #         print("Touch sound option is present in the complete image.")
    #         if max_val_on > max_val_off:
    #             print("Touch sound is ON.")
    #             return "PASS"
    #         else:
    #             print("Touch sound is OFF.")
    #             return "FAIL"
    #     else:
    #         print("Touch sound option is not found in the complete image.")
    #         return "FAIL"

# # Usage
# testimage = 'path/to/testimage.png'
# ref_on_image = 'path/to/reference_on_image.png'
# ref_off_image = 'path/to/reference_off_image.png'
# result = button_on_off(testimage, ref_on_image, ref_off_image)
# print("Test result:", result)

# if __name__ == '__main__':
#     x = ADBController()
#     x.delay(2)

    #x.findtext()
    #x.tap(689,28)
    #x.findtext("D:\TAF_ADB\screenshots\Home.png")
    #testimage="D:\\TAF_ADB\\screenshots\\Testimage_Touch_sound.png"
    #ref_on_image="D:\\TAF_ADB\\refernce\\Gentralsettings_page.png"
    #ref_off_image="D:\\TAF_AD\\refernce\\Gentral_Settings_Touch_OFF.png"
    #tes="D:\\TAF_ADB\\Verify.png"
    #x.button_on_off(testimage,ref_on_image)