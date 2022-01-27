from PIL import Image
import pytesseract
import re
import io
import requests


# pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

class ImageOcr:

    tel = ''
    fax = ''
    email = ''
    
    def _read_img(self, url):
        with requests.Session() as s:
            try:
                r = s.get(url, stream=True)
                byteImgIO = io.BytesIO(r.content)
                img = Image.open(byteImgIO)
                img_crop = img.crop((410, 205, 750, 405))
                reader = pytesseract.image_to_string(img_crop, lang='rus+eng')
                return reader
            except Exception:
                return '0'

    def exstract_data(self, url):
        file_data = self._read_img(url)
        if file_data != '0':
            format_data = ' '.join(file_data.split())
            try:
                tel = re.search(r'(\+7|8|)[\s(]*\d{3}[)\s]*\d{3}[\s-]?\d{2}[\s-]?\d{2}', format_data)
                self.tel = (tel.group(0))
            except AttributeError:
                self.tel = 'данные не распознаны'
            try:
                fax = re.search(r'Факс:\s[(]*\d{3}[)]\s\d{3}[\s-]\d{2}[\s-]\d{2}', format_data)
                self.fax = (fax.group(0))
            except AttributeError:
                self.fax = 'данные не распознаны'
            try:
                email = re.search(r'\w+@\w+\.\w+', format_data)
                self.email = (email.group(0))
            except AttributeError:
                self.email = 'данные не распознаны'
            return self.tel, self.fax, self.email
        else:
            return 'ошибка при загрузке', 'ошибка при загрузке', 'ошибка при загрузке'

