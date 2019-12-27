from mycroft import MycroftSkill
from mycroft.skills.common_play_skill import CommonPlaySkill, CPSMatchLevel
from mycroft.util.parse import match_one
from mycroft.audio import wait_while_speaking
from datetime import datetime, timedelta
import feedparser
import requests

phrase_dict = {
    'all india radio': 'national',
    'national news on all india radio': 'national',
    'local news on all india radio': 'local',
    'regional news on all india radio': 'local'
}
category = {
    'local': 'http://newsonair.nic.in/Regional_Audio_rss.aspx',
    'national': 'http://newsonair.nic.in/NSD_Audio_rss.aspx'
}
language = {
    'eng': 'English',
    'hin': 'Hindi',
    'urd': 'Urdu',
    'asm': 'Assamese',
    'ben': 'Bengali',
    'dog': 'Dogri',
    'guj': 'Gujarati',
    'kan': 'Kannada',
    'kas': 'Kashmiri',
    'kon': 'Konkani',
    'mal': 'Malayalam',
    'mar': 'Marathi',
    'nep': 'Nepali',
    'odi': 'Odia',
    'pun': 'Punjabi',
    'san': 'Sanskrit',
    'tam': 'Tamil',
    'tel': 'Telugu'
}
station = {
    'aga-kok': 'Agartala-Kokborok',
    'aga-ben': 'Agartala-Bengali',
    'ahm-guj': 'Ahmedabad-Gujarati',
    'ahm-sin': 'Ahmedabad-Sindhi',
    'aiz-miz': 'Aizawl-Mizo',
    'aur-mar': 'Aurangabad-Marathi',
    'aur-urd': 'Aurangabad-Urdu',
    'ban-kan': 'Bangalore-Kannada',
    'bho-hin': 'Bhopal-Hindi',
    'bhu-guj': 'Bhuj-Gujarati',
    'cal-mal': 'Calicut-Malayalam',
    'cha-hin': 'Chandigarh-Hindi',
    'cha-pun': 'Chandigarh-Punjabi',
    'che-tam': 'Chennai-Tamil',
    'cut-odi': 'Cuttack-Odia',
    'deh-hin': 'Dehradun-Hindi',
    'dha-kan': 'Dharwad-Kannada',
    'dib-asm': 'Dibrugarh-Assamese',
    'gan-nep': 'Gangtok-Nepali',
    'gan-lep': 'Gangtok-Lepcha',
    'gan-bhu': 'Gangtok-Bhutia',
    'gor-hin': 'Gorakhpur-Hindi',
    'gor-bho': 'Gorakhpur-Bhojpuri',
    'guw-asm': 'Guwahati-Assamese',
    'guw-kar': 'Guwahati-Karbi',
    'guw-nep': 'Guwahati-Nepali',
    'guw-bod': 'Guwahati-Bodo',
    'hyd-tel': 'Hyderabad-Telugu',
    'hyd-urd': 'Hyderabad-Urdu',
    'imp-man': 'Imphal-Manipuri',
    'ita-hin': 'Itanagar-Hindi',
    'ita-eng': 'Itanagar-English',
    'jai-hin': 'Jaipur-Hindi',
    'jai-raj': 'Jaipur-Rajasthani',
    'jam-goj': 'Jammu-Gojri',
    'jam-dog': 'Jammu-Dogri',
    'koh-nag': 'Kohima-Nagamese',
    'koh-eng': 'Kohima-English',
    'kol-ben': 'Kolkata-Bengali',
    'kur-nep': 'Kurseong-Nepali',
    'leh-lad': 'Leh-Ladakhi',
    'luc-hin': 'Lucknow-Hindi',
    'luc-urd': 'Lucknow-Urdu',
    'mum-mar': 'Mumbai-Marathi',
    'nag-mar': 'Nagpur-Marathi',
    'pan-kon': 'Panaji-Konkani',
    'pat-hin': 'Patna-Hindi',
    'pat-mai': 'Patna-Maithili',
    'pud-tam': 'Pudducherry-Tamil',
    'pun-mar': 'Pune-Marathi',
    'rai-chh': 'Raipur-Chhatisgar',
    'rai-hin': 'Raipur-Hindi',
    'ran-hin': 'Ranchi-Hindi',
    'sam-sam': 'Sambalpur-Sambalpuri',
    'shi-jai': 'Shillong-Jaintia',
    'shi-eng': 'Shillong-English',
    'shi-kha': 'Shillong-Khasi',
    'shi-gar': 'Shillong-Garo',
    'shi-hin': 'Shimla-Hindi',
    'sil-ben': 'Silchar-Bengali',
    'tir-tam': 'Tiruchirapalli-Tamil',
    'thi-mal': 'Thiruvanantapuram-Malayalam',
    'vij-tel': 'Vijayawada-Telugu',
    'vis-tel': 'Visakhapatnam-Telugu'
}


class AllIndiaRadio(CommonPlaySkill):
    #def __init__(self):
    #    MycroftSkill.__init__(self)

    def CPS_match_query_phrase(self, phrase):
        """ This method responds whether the skill can play the input phrase.
            The method is invoked by the PlayBackControlSkill.
            Returns: tuple (matched phrase(str),
                            match level(CPSMatchLevel),
                            optional data(dict))
                     or None if no match was found.
        """
        match, confidence = match_one(phrase, phrase_dict)
        if confidence > 0.8:
            return (match, CPSMatchLevel.EXACT, {'categ': match})
        else:
            return None


    def CPS_start(self, phrase, data):
        """ Starts playback.
            Called by the playback control skill to start playback if the
            skill is selected (has the best match level)
        """
        rss_parsed = feedparser.parse(category[data['categ']].strip()) # strip uri of leading and trailing spaces before parsing
        dt_now = datetime.now()
        bd = timedelta(hours=24)
        if data['categ'] == 'local':
            for e in rss_parsed.entries:
                if station[self.settings.get('station')] in e.title:
                    bt = datetime.strptime(e.published+e.bulletintime, "%b %d, %Y%H%M")
                    if bd > dt_now - bt:
                        bd = dt_now - bt
                        link = requests.get(e.enclosures[0].href)
                        break
        elif data['categ'] == 'national' and self.settings.get('language') == 'eng':
            for e in rss_parsed.entries:
                if e.author == 'English' and (('Morning' in e.title) or ('Midday'in e.title) or ('Nine'in e.title)):
                    bt = datetime.strptime(e.published+e.bulletintime, "%b %d, %Y%H%M")
                    if bd > dt_now - bt:
                        bd = dt_now - bt
                        link = requests.get(e.enclosures[0].href)
                        break
        elif data['categ'] == 'national':
            for e in rss_parsed.entries:
                if e.author == language[self.settings.get('language')]:
                    bt = datetime.strptime(e.published+e.bulletintime.split('-')[0], "%b %d, %Y%H%M")
                    if bd > dt_now - bt:
                        bd = dt_now - bt
                        link = requests.get(e.enclosures[0].href)
                        break
        url = link.url.replace('https', 'http', 1) # replace 'https' with 'http'
        self.log.info(url)
        self.speak('Playing the latest news bulletin from All India Radio:')
        wait_while_speaking()
        self.CPS_play(url)


def create_skill():
    return AllIndiaRadio()
