from main import Bot

bot = Bot('fkisfshonvtpcvdnnaxflfdwmhsnqmpa')
guid = 'u0BvgeO050cba0d18909403ab52d63b4'

previous_time = 'None'

while (True):
    try:
        if previous_time != bot.get_time():
            current_time = bot.get_time()
    
            avatar_id = bot.getAvatars(guid)['avatars']
            bot.uploadAvatar(guid, bot.clock_image(current_time))
            if avatar_id == []:
                continue
            bot.deleteAvatar(guid, avatar_id[0]['avatar_id'])
            previous_time = current_time
    except: ...