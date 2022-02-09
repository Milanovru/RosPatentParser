from PIL import Image
import pytesseract
import re
import io
import requests

#pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

class ImageOcr:

    tel = ''
    fax = ''
    email = ''
    
    def _read_img(self, url):
        with requests.Session() as s:
            try:
                r = s.get(url, stream=True)
                byteImgIO = io.BytesIO(r.content)
                img = Image.open(byteImgIO).convert('RGB')
                img_crop = img.crop((405, 205, 760, 428))
                reader = pytesseract.image_to_string(img_crop, lang='rus+eng')
                return reader
            except Exception:
                return None

    def exstract_data(self, url) -> str:
        file_data = self._read_img(url)
        if file_data != None:
            format_data = ' '.join(file_data.split()).lower()
            try:
                #(\+7|8|)[\s(]*\d{3}[)\s]*\d{3}[\s-]?\d{2}[\s-]?\d{2}
                tel = re.search(r'(?:\+|\d)[\d\-\(\)]{8,}\d', format_data)
                self.tel = tel.group(0)
            except AttributeError:
                self.tel = '-'
            try:
                start_idx = re.search(r'факс: |факс ', format_data)
                end_idx = re.search(r'e-mail: |e-mail ', format_data)
                search_fax = format_data[start_idx.end():end_idx.start()]
                fax = re.search(r'(?:\+|\d)[\d\-\(\)]{8,}\d', search_fax)
                self.fax = fax.group(0)
            except AttributeError:
                self.fax = '-'
            try:
                start_idx = re.search(r'e-mail: |e-mail ', format_data)
                if start_idx is None:
                    self.email = self._analyze_text(format_data)
                else:
                    chank_data = format_data[start_idx.end():]
                    self.email = self._analyze_text(chank_data)
            except AttributeError:
                self.email = '-'
            return self.tel, self.fax, self.email
        else:
            return self.tel, self.fax, self.email
        
    def _analyze_text(self, data: str) -> str:
        words = []
        word = ''
        for let in data:
            check = re.search(r'[a-z]|\@|\.', let)
            if check:
                word += let
            elif let == ' ':
                if word != '':
                    words.append(word)
                word = ''

        variants = ()

        for idx,word in enumerate(words):
            if word.find('@') != -1:
                variants = (word, word + words[idx+1] + ' ' + word + words[idx-1])
                break
        try:
            re_text = re.sub(r'\.', '_', variants[0])
            email_text = re.search(r'\w+\@\w+\_\w+', re_text)
            if email_text is None:
                email_text = re.search(r'\w+\@\w+', variants[0])
            find_text = email_text.group(0)
            return find_text.replace('_', '.')
        except:
            re_text = re.sub(r'\.', '_', variants[1])
            email_text = re.search(r'\w+\@\w+\_\w+', re_text)
            if email_text is None:
                email_text = re.search(r'\w+\@\w+', variants[1])
            find_text = email_text.group(0)
            return find_text.replace('_', '.')
