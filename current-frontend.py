import PySimpleGUI as sg
import time
time.clock = time.time
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from PIL import Image
import io

chatbot = ChatBot('Ron Obvious')

# Create a new trainer for the chatbot
chatbot.set_trainer(ChatterBotCorpusTrainer)

# Train based on the english corpus
#chatbot.train("chatterbot.corpus.english")

# Train based on english greetings corpus
#chatbot.train("chatterbot.corpus.english.greetings")

# Train based on the english conversations corpus
#chatbot.train("chatterbot.corpus.english.conversations")
chatbot = ChatBot('Ron Obvious', trainer='chatterbot.trainers.ChatterBotCorpusTrainer')

# Train based on the english corpus
# chatbot.train("chatterbot.corpus.english")

################# GUI #################
image = Image.open(r'C:\Users\Brandon\Downloads\Logo ONLY.png')
image.thumbnail((200, 200))
bio = io.BytesIO()
image.save(bio, format="PNG")

layout = [[sg.Text('SHELLY: How can I help you?', size=(40,2), justification='left', background_color="#272533", text_color='white', font=('Lora', 14, 'bold')),
          sg.Image(r'C:\Users\Brandon\Downloads\Logo ONLY (2).png', )],
        [sg.Multiline(size=(80, 20), reroute_stdout=True, echo_stdout_stderr=True)],
          [sg.MLine(size=(70, 5), key='-MLINE IN-', enter_submits=True, do_not_clear=False),
           sg.Button('SEND', bind_return_key=True), sg.Button('EXIT')]]

window = sg.Window('SHELLY', layout,
            default_element_size=(30, 2))
# ---===--- Loop taking in user input and using it to query HowDoI web oracle --- #
while True:
    event, values = window.read()
    if event != 'SEND':
        break
    string = values['-MLINE IN-'].rstrip()
    print('  ' + string)
    # send the user input to chatbot to get a response
    response = chatbot.get_response(values['-MLINE IN-'].rstrip())
    print(response)