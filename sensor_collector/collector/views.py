from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from rest_framework.decorators import api_view

from collector.models import AudioRecord

import os
import json
import socket


RESPONSE = """
    <p>Collecting Audio Data</p>

    <script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js"></script>
    <script type="text/javascript">
        var user_name = prompt("User Name:", "Tester");
        if (user_name != null) {
            window.AudioContext = window.AudioContext || window.webkitAudioContext;
            var context = new AudioContext();
            var analyser = context.createAnalyser();
            analyser.fftSize = 256;
            analyser.frequencyBinCount = 128;

            navigator.webkitGetUserMedia({ audio: true }, function (stream) {
                var source = context.createMediaStreamSource(stream);
                source.connect(analyser);
                analyser.connect(context.destination);

                setInterval(function () {
                    var ts = (new Date).getTime();
                    var freq_array = new Uint8Array(analyser.frequencyBinCount);
                    var time_array = new Uint8Array(analyser.fftSize);
                    analyser.getByteFrequencyData(freq_array);
                    analyser.getByteTimeDomainData(time_array);
                    console.log((new Date).getTime());
                    console.log(freq_array);
                    console.log(time_array);

                    // should call API to send data back to server
                    $.ajax({
                        url: "http://localhost:8000/collector/upload_data/",
                        type: "POST",
                        data: { user: user_name, ts: ts, fft: JSON.stringify(freq_array), td: JSON.stringify(time_array)},
                        dataType: "json",
                    });
                }, 1000);
            }, function () { });
        }
    </script>
"""


# Create your views here.
def index(request):
    return HttpResponse(RESPONSE)


@api_view(['GET', 'POST'])
def upload_data(request):
    print(request.method)
    user = str(request.data['user'])
    ts = long(request.data['ts'])
    fft_json = json.loads(request.data['fft'])
    td_json = json.loads(request.data['td'])
    # preprocess fft_json and td_json
    fft = list()
    td = list()

    for i in range(0, len(fft_json)):
        key = str(i)
        fft.append(fft_json[key])

    for i in range(0, len(td_json)):
        key = str(i)
        td.append(td_json[key])

    audio_record = AudioRecord.objects.create(
        user_name=user,
        timestamp=ts,
        fft_vector=str(fft),
        td_vector=str(td))
    audio_record.save()

    # save data into file
    # TODO: will have thread safe problem. Should store data into database
    # dir = "data/audio"
    # if not os.path.exists(dir):
    #     os.makedirs(dir)
    # f = open(dir + "/" + user + ".json", 'a')
    # f.write(json.dumps(request.data) + "\n")

    return HttpResponse("uploading done!")
