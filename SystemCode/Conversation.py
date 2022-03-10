class Conversation:
    def __init__(self, chatid = None, username=None, emotion=None, category=None):
        self.chatid = chatid
        self.username = username
        self.emotion = emotion
        self.category = category

    def set_id_username(self, chatid, username):
        self.chatid = chatid
        self.username = username

    def set_emotion(self, emotion):
        self.emotion = emotion

    def set_category(self, category):
        self.category = category

    def get_username(self):
        return self.username

    def get_emotion(self):
        return self.emotion

    def get_category(self):
        return self.category

    def get_chatid(self):
        return self.chatid

