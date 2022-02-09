import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import time
from .imageocr import ImageOcr
from .exelwriter import ExelWriter
from tkinter import *
from tkinter import messagebox
from tkinter import scrolledtext
from threading import Thread
from loguru import logger
import sys


proxies = open('proxy.txt').read().split('\n')
ua = UserAgent()

logger.add(f'logs/logs.log', format='{time} {level} {message}',
    level='DEBUG', rotation='500 MB',
    compression='zip')

def clicked():
    html = Parser(int(ent1.get()), int(ent2.get()))
    th1 = Thread(target=html.parse, name='requests')
    th1.start()

def set_info(text):
    txt.insert(INSERT, text)
    
def clear_info():
    txt.delete('1.0', END)
    
app = Tk()
app.title('RusPatentParser v0.2.4.1')
app.geometry("500x400")
app.grid_rowconfigure(0, weight=0)

lab1 = Label(app, text="Начальный индекс:", width=20)
lab1.grid(column=0, row=0, padx=5, pady=5)
lab2 = Label(app, text="Конечный индекс:")
lab2.grid(column=0, row=1, padx=5, pady=5)

ent1 = Entry(app, width=15)
ent1.grid(column=1, row=0)
ent1.focus()
ent2 = Entry(app, width=15)
ent2.grid(column=1, row=1)

txt = scrolledtext.ScrolledText(app, width=60, height=15)
txt.grid(column=0, row=3, columnspan=3)

btn = Button(app, text='Поиск', command=clicked)
btn.grid(column=0, row=4, pady=20)

class Parser:
    
    document_data = []   
    start_index = 0
    end_index = 0
    LEN = 0
    COUNT = 1

    number = ''
    applicant = ''
    representative = 'не является патентным поверенным'
    address = ''
    status = ''
    data = ''

    image_ocr = ImageOcr()
    exel_writer = ExelWriter()
   
    def __init__(self, start_index: int, end_index: int):
        self.start_index = start_index
        self.end_index = end_index
        self.LEN = end_index - start_index
        
    def _get_data(self, html):
            doc = html.find('td', {'class': 'White'})
            doc_list = html.find_all('p', {'class': 'bib'})
            # Принято решение об отказе в регистрации (последнее изменение: 20.08.2020)
            text = ' '.join(doc.text.split())[28:]
            check = text.find('Принято решение об отказе в регистрации')
            if check != -1:
                set_info('Парсинг страницы...\n')
                self.status = text[:39]
                self.data = text[62:-1]
                for item in doc_list:
                    valid_data = ' '.join(item.text.split())
                    if valid_data[1:4] == '210':
                        self.number = item.find('b').text
                    if valid_data[1:4] == '540':
                        url = item.find('a').get('href')[:-3]
                        link_gif = url+'GIF'
                    if valid_data[1:4] == '731':
                        self.applicant = item.find('b').text
                    if valid_data[1:4] == '740':
                        self.representative = item.find('b').text
                    if valid_data[1:4] == '750':
                        self.address = item.find('b').text  # 191186, Санкт-Петербург, а/я 142, Н.И. Петровой
                set_info('Обработка изображения...\n')
                img_data = self.image_ocr.exstract_data(link_gif)
                self.document_data.append({
                    'id': self.number,
                    'status': self.status,
                    'data': self.data,
                    'applicant': self.applicant,
                    'representative': self.representative,
                    'address': self.address,
                    'phone': img_data[0],
                    'fax': img_data[1],
                    'email': img_data[2]
                })
                self.number = ''
                self.applicant = ''
                self.representative = 'не является патентным поверенным'
                self.address = ''
                self.status = ''
                self.data = ''
        
    def parse(self):
        proxy_idx = 0
        proxy_len = len(proxies)
        proxy = {'http': f'http://{proxies[proxy_idx]}'}
        with requests.Session() as s:
            s.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0'})
            for id in range(self.start_index, self.end_index+1):
                set_info(f'Страница {self.COUNT}/{self.LEN+1}\n')
                #http://icanhazip.com/
                url = f'https://www1.fips.ru/registers-doc-view/fips_servlet?DB=RUTMAP&DocNumber={id}&TypeFile=html'
                r = s.get(url=url)
                if r.status_code == 200: 
                    soup = BeautifulSoup(r.text, 'lxml')
                    if soup.text  == 'Документ с данным номером отсутствует':
                        logger.warning(f'№ {id}:{soup.text}')
                    elif soup.text == 'Слишком быстрый просмотр документов.':
                        logger.warning(f'№ {id}:{soup.text}')
                        set_info(f"Получено предупреждение о слишком быстром просмотре документа. Делаю паузу 10 секунд\n")
                        time.sleep(10)
                        try:
                            self._get_data(soup)
                        except Exception as e:
                            logger.error(f'№ {id}: {e}')
                            messagebox.showinfo('Системное сообщение', 'Аварийная остановка приложения.')
                            break
                    elif soup.text == 'Превышен допустимый предел количества просмотров документов из реестра в день.':
                        logger.warning(f'№ {id}:{soup.text}')
                        proxy_idx += 1
                        if proxy_idx <= proxy_len:
                            logger.info('изменен proxy')
                            continue
                        else:
                            messagebox.showinfo('Системное сообщение', 'Закончились proxy. Превышен допустимый предел количества просмотров документов.')
                            break    
                    else:
                        try:
                            self._get_data(soup)
                        except Exception as e:
                            logger.error(f'№ {id}: {e}')
                            messagebox.showinfo('Системное сообщение', 'Аварийная остановка приложения.')
                            break             
                else:
                    set_info(r.status_code)
                    sys.exit()
                self.COUNT += 1
                set_info('Ожидание следующего подключения...\n')
                time.sleep(4)
                if id % 3 == 0:  # чистит экран
                    clear_info()
                
        self._create_document()
        self.document_data = []
        self.LEN = 0
        self.COUNT = 1

    def _create_document(self):
        data = self.exel_writer.generate_data(self.document_data)
        try:
            set_info('идет запись в файл\n')
            self.exel_writer.write_to_exel(data)
            messagebox.showinfo('Системное сообщение', 'Обработка завершена: результаты сохранены в файле output_data.xlsx!')
        except Exception as e:
            messagebox.showinfo('Системное сообщение', 'Ошибка при записи в файл!')
            logger.error(e)
