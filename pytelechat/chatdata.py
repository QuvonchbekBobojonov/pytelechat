import requests
from bs4 import BeautifulSoup
from pytelechat.errors import TelegramChatDataError

       

class GetChat:
    def __init__(self, url) -> None:
        self.__url = url
    
    def __is_telegram_chat_type(self, chat: str):
        if chat:
            chat: str = chat.split(',')[0]
            if chat.endswith('subscribers'):
                return 'channel'
            elif chat.endswith('members'):
                return 'group'
            elif chat.endswith('member'):
                return 'group'
            else:
                raise TelegramChatDataError('Chat type not verified')
        else:
            return 'member'


    def __get_telegram_chat_data(self, url: str):
        data: dict = {}
        res = requests.get(url)
        soup = BeautifulSoup(res.content, 'html.parser')
        try:
            name: str = soup.find_all(class_="tgme_page_title")[0].text.split('\n')[1]
            tgme_page_extra: str = soup.find_all(class_="tgme_page_extra")[0].text
            tgme_page_photo_image: str = soup.find_all(class_="tgme_page_photo_image")[0].get('src')
        except IndexError:
            name: str = None
            tgme_page_extra: str = None
            tgme_page_photo_image: str = None
        type_: str = self.__is_telegram_chat_type(tgme_page_extra)

        private: bool = self.__get_telegram_chat_private(url)
        if type_ == 'member':
            data['name']: str = soup.find_all(class_="tgme_page_title")[0].text.split('\n')[0]
        else:
            data['name'] = name
        if type_ == 'channel':
            data['subscribers'] = int(tgme_page_extra.replace('subscribers', ''))
        if type_ == 'group':
            if tgme_page_extra.endswith('online'):
                tg_mem = tgme_page_extra.split()
                num = next((num for num in tg_mem if num == 'members'), None)
                data['online'] = tg_mem[-2]

            data['members'] = self.__get_members(tgme_page_extra.split())
            

        data['type']: str = type_
        data['private']: bool = private
        if type_ == 'member':
            data['photo_url']: str = soup.find_all(class_="tgme_page_photo_image")[0].get('src')
        else:
            data['photo_url'] = tgme_page_photo_image
        
        try:
            data['description'] = soup.find_all(class_="tgme_page_description")[0].text
        except IndexError:
            pass
        return data


    def __get_telegram_chat_private(self, chat: str):
        data = chat.split("https://t.me/")[1]
        private: bool = True if data[0] == '+' else False
        return private
    
    def __get_members(self, data):
        num = ''
        for item in data:
            if item == 'members,' or item == 'members' or item == 'member':
                break
            num += item

        return int(num)
    
    def data(self):
        return self.__get_telegram_chat_data(self.__url)