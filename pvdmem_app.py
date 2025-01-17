# Flask app for pvdmem (packet-via-dmem parser)
import string
import random
import sys
import subprocess
from pvdmem import parse_raw_dump, make_clear_parsels, create_pcap
from flask import Flask, request, Request, render_template, send_file, after_this_request
from datetime import datetime, timezone

# Random sequence parameters for filename
random_length = 8
characters = string.ascii_letters + string.digits

# Class for supporting big requests in flask
class CustomRequest(Request):
    def __init__(self, *args, **kwargs):
        super(CustomRequest, self).__init__(*args, **kwargs)
        self.max_form_memory_size = 10000000

app = Flask(__name__)
app.request_class = CustomRequest

# Main flask app
@app.route('/', methods=['GET', 'POST'])
def index():

    pcap_result = ''  # Result of text2pcap
    txt_file = ''
    pcap_file = ''

    if request.method == 'GET':
        return render_template('index.html')
    
    elif request.method == 'POST':

        # Valued data from form.
        pcap_text = request.form.get('pcap_text')
        parse_direction = request.form.get('parse_direction')
        button_name = list(request.form.keys())[2]

        # print(request.form, file=sys.stderr)

        if button_name == "create_pcap":
            
            # Generate random session ID (used for filename)
            session = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S") + \
                    ''.join(random.choice(characters) for _ in range(random_length))
            
            txt_file = '.txts/' + session + '.txt'
            pcap_file = '.pcaps/'+ session + '.pcap'
            
            # Parse pasted data 
            parsed = parse_raw_dump(pcap_text.split('Wallclock: '))
            
            # Choose direction of pcap according radio button selection
            if parse_direction == 'toLU':
                cleared = make_clear_parsels(parsed, fromLU=False)
            elif parse_direction == 'fromLU':
                cleared = make_clear_parsels(parsed, toLU=False)
            else:
                cleared = make_clear_parsels(parsed)

            # Create pcap file if we have non-zero list of cleared data
            if cleared:
                pcap_result = create_pcap(cleared, txt_file, pcap_file)
                
                @after_this_request
                def delete_pcap(response):
                    try:
                        remove_result = subprocess.run(["rm", pcap_file])
                    except Exception as ex:
                        print(ex, file=sys.stderr)
                    
                    return response

                return send_file(pcap_file,
                            mimetype='application/vnd.tcpdump.pcap',
                            download_name='pvdmem.pcap',
                            as_attachment=True)
            else:
                return render_template('index.html',
                               form_text = pcap_text,
                               log_text = 'No data for PCAP found')


        elif button_name == "clear_text":
            return render_template('index.html',
                               is_dnld_disabled = "disabled")
        

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='5000')