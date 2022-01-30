from PIL import Image
import pytesseract
import re
import io
import requests


pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

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
                img_crop = img.crop((405, 205, 760, 428))
                reader = pytesseract.image_to_string(img_crop, lang='rus+eng')
                return reader
            except Exception:
                return '0'

    def exstract_data(self, url):
        file_data = self._read_img(url)
        if file_data != '0':
            format_data = ' '.join(file_data.split()).lower()
            try:
                tel = re.search(r'(\+7|8|)[\s(]*\d{3}[)\s]*\d{3}[\s-]?\d{2}[\s-]?\d{2}', format_data)
                self.tel = tel.group(0)
            except AttributeError:
                self.tel = ''
            try:
                start_idx = re.search(r'факс: |факс ', format_data)
                end_idx = re.search(r'e-mail: |e-mail ', format_data)
                search_fax = format_data[start_idx.end():end_idx.start()]
                fax = re.search(r'(\+7|8|)[\s(]*\d{3}[)\s]*\d{3}[\s-]?\d{2}[\s-]?\d{2}', search_fax)
                self.fax = fax.group(0)
            except AttributeError:
                self.fax = ''
            try:
                start_idx = re.search(r'e-mail: |e-mail ', format_data)
                format_data = format_data[start_idx.end():]
                re_text = re.sub(r'\.', '_', format_data)
                text = re.search(r'\w+[@|\s@]\w+\_\w+', re_text)
                email = text.group(0)
                self.email = email.replace('_', '.')
            except AttributeError:
                self.email = '-'
            return self.tel, self.fax, self.email
        else:
            return 'ошибка при загрузке', 'ошибка при загрузке', 'ошибка при загрузке'

