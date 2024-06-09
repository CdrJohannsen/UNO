#!/usr/bin/env python
import os
from hashlib import md5
from time import time

from flask import Flask, make_response, request, send_from_directory
from flask_socketio import SocketIO, emit

from cards import *
from logic import *

app = Flask(__name__, static_folder="static/", static_url_path="/")
socketio = SocketIO(app)

def render_cards(cards: list) -> str:
    form = """
    <title>Uno</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.5.1/jquery.min.js" integrity="sha512-bLT0Qm9VnAYZDflyKcBaQ2gg0hSYNQrJ8RilYldYQ1FxQYoCLtUjuuRuZo+fjqhx/qtq/1itJ0C2ejDxltZVFg==" crossorigin="anonymous"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/3.0.4/socket.io.js" integrity="sha512-aMGMvNYu8Ue4G+fHa359jcPb1u+ytAF+P2SCb+PxrjCdO3n3ZTxJ30zuH39rimUggmTwmh2u7wvQsDTHESnmfQ==" crossorigin="anonymous"></script>
    <script type="text/javascript" charset="utf-8">
        function getCookie(cname) {
            let name = cname + "=";
            let decodedCookie = decodeURIComponent(document.cookie);
            let ca = decodedCookie.split(';');
            for(let i = 0; i <ca.length; i++) {
                let c = ca[i];
                while (c.charAt(0) == ' ') {
                    c = c.substring(1);
                }
                if (c.indexOf(name) == 0) {
                    return c.substring(name.length, c.length);
                }
            }
            return null;
        }
    

        var socket = io();
        let last_card = null;
        let users = null;
        function useCard(card_id) {
            socket.emit('card_use',{id:card_id}); 
        };

        function drawCard() {
            socket.emit('draw_card'); 
        };

        function disableAll() {
            for (i=0;i<108;i++) {
                var element = document.getElementById(i);
                element.disabled = true;
            }
        }

        function enableAll() {
            for (i=0;i<108;i++) {
                var element = document.getElementById(i);
                element.disabled = false;
            }
        }

        socket.on("card_used",function(data){
            var element = document.getElementById(data.id);
            element.style.position = "absolute";
            element.style.left = "50% - 35px";
            element.style.top = "25px"
            element.style.display = "block";
            element.disabled = true;
            if (last_card != null) {
                var element = document.getElementById(last_card);
                element.style.display = "none";
            }
            last_card = data.id;
        });

        socket.on("receive_card",function(data){
            var element = document.getElementById(data.id);
            element.style.position = "static";
            element.style.top = "0px";
            element.style.display = "block";
            element.disabled = false;
        });

        socket.on("card_removed",function(data){
            var element = document.getElementById(data.id);
            element.style.top = "0px";
        });

        socket.on("draw_update",function(data){
            var element = document.getElementById("draw_counter");
            if (data.number != 0) {
                element.innerHTML = data.number;
            }
            else {
                element.innerHTML = "";
            }
        });

        socket.on("set_user",function(data){
            var user_list = document.getElementById("users");
            user_list.innerHTML = ""
            for (var key in users){
                user_list.innerHTML += "<span id="+key+" style='margin:20px;'>"+users[key]+"</span>"
            }
            document.getElementById(data.user_id).style.color = "#ffffff";
            document.getElementById(getCookie("UserID")).style.textDecoration = "underline";
        })

        socket.on("start",function(data){
            document.getElementById('start_button').remove();
            document.getElementById('draw_button').disabled = false;
            enableAll();
            users = data.users
        });

        if (getCookie("Username") == null){
            document.cookie = "Username="+prompt("Username")+";";
        }


    </script>
    <style>
    @font-face {font-family:Cabin ; src:url('Cabin-Bold.ttf')}
    body {
        background-color: #555555;
        height: 100%;
        width: 100%;
        margin: 0px;
        font-family:Cabin;
        font-size: 20px;
        text-align:center;
        justify-content:center;
    }
    .card {
        position: static;
        border-radius: 14px;
        padding: 0px;
        margin: 2px;
        border-width: 2px;
        border-color: black;
        border-style: solid;
    }
    </style>
    
    <p id="users"><button id="start_button" onclick="socket.emit('start');">Start</button></p>
    <br>
    <br style="line-height: 200px;">
    <br>
    <button id="draw_button" onclick="drawCard()">Draw <span id="draw_counter"></span></button>
    <br>
    <div style="display: flex; flex-wrap:wrap;justify-content:center;">
    """
    for card in game.all_cards:
        form += f"""
<button name="{card.get_description()}" onclick="useCard({card.id})" id="{card.id}" class="card" style="background:{card.color.value}; display: {'none' if not card in cards else 'block'}"><img src="{card.get_image()}" alt="{card.get_description()}" style="width: 66px;height: 100px;"></button>"""
    form += "</div>"
    form += """<script type="text/javascript" charset="utf-8">
        disableAll();
        document.getElementById('draw_button').disabled = true;
        const lock = document.createElement('meta');
lock.name = 'darkreader-lock';
document.head.appendChild(lock);
    </script>"""
    return form


@socketio.on("start")
def handle_start():
    emit("start", {"users": game.users}, broadcast=True)
    for i in range(len(game.draw_pile)):
        if game.draw_pile[i].card_type.value < 10:
            game.discard_pile.append(game.draw_pile.pop(i))
            break
    emit("card_used", {"id": game.discard_pile[-1].id}, broadcast=True)
    set_user(request.cookies.get("UserID"))


@socketio.on("draw_card")
def handle_draw_card():
    user_id = request.cookies.get("UserID")
    for i in range(max(1, game.draw_number)):
        draw_card(user_id)
    reset_draw()


@socketio.on("card_use")
def handle_card_use(json):
    user_id = request.cookies.get("UserID")
    if can_play_card(user_id, json["id"]):
        play_card(user_id, json["id"])
        emit("card_removed", json)
        emit("card_used", json, broadcast=True)


@app.route("/", methods=["GET"])
def index():
    resp = make_response()
    if not (user_id := request.cookies.get("UserID")) or not user_id in game.users:
        user_id = md5((str(request.remote_addr) + str(time())).encode()).hexdigest()
        game.cards[user_id] = []
        game.users[user_id] = request.cookies.get("Username")
        print(f"[USER CONNECTED] username={game.users[user_id]}, ip={request.remote_addr}, {user_id=}")
        for i in range(10):
            game.cards[user_id].append(game.draw_pile.pop())
        resp.set_cookie("UserID", user_id)
    resp.set_data(render_cards(game.cards[user_id]))
    return resp


if __name__ == "__main__":
    socketio.run(app=app, host="::", port=8080, debug=True, use_reloader=True, log_output=True)
