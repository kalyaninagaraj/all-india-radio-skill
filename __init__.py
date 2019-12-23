from mycroft import MycroftSkill, intent_file_handler


class AllIndiaRadio(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('radio.india.all.intent')
    def handle_radio_india_all(self, message):
        self.speak_dialog('radio.india.all')


def create_skill():
    return AllIndiaRadio()

