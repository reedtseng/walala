def process_command(command):

    response = f"指令內容: {command}\n"
    match command:
        case value if "追蹤清單" in value:
            response += list_tracks()
        case value if value.startswith('新增追蹤'):
            track_body = value[4:]
            response += add_track(track_body)
        case value if value.startswith('刪除追蹤'):
            stock = value[4:]
            response += remove_track(stock)
        case value if "近期" in value:
            stock = value[:4]
            response += short_term_outloop(stock)
        case _:
            # message = chat_llm.predict_messages([
            #     SystemMessage(
            #         content=f"""Your name is 'Walala' or simply 'Wala'. You are a amiable stock-track bot.
            #         You were reborn on {time.ctime()} and were asleep before then.
            #         As long as you don’t interact with anyone for more than 15 minutes, you will fall asleep again."""),
            #     HumanMessage(content=command)
            # ]).content
            message = open_ai_agent.run(command)
            response += ("\n" + message)
    return response
