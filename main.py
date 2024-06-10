#!/usr/bin/env python
import os
from hashlib import md5
from time import time

from flask import Flask, make_response, request
from flask_socketio import SocketIO, emit

from cards import *
from logic import *

app = Flask(__name__, static_folder="static/", static_url_path="/")
socketio = SocketIO(app)


def render_cards() -> str:
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

        function hideAll() {
            for (i=0;i<108;i++) {
                var element = document.getElementById(i);
                element.style.display = "none";
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
            element.style.top = "45px"
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
            document.getElementById(data.user_id).style.color = "highlight";
            var own_name = document.getElementById(socket.id)
            if (own_name != null){
                own_name.style.textDecoration = "underline";
            }
        });

        socket.on("update_leaderboard",function(data) {
            leaderboard = document.getElementById('leaderboard');
            leaderboard.innerHTML = ""
            for (var key in data) {
                leaderboard.innerHTML += `<p>${key}: ${data[key]}</p>`
            }
        });

        socket.on("player_won",function(data){
            delete users[data.winner]
        });

        socket.on("game_over",function(data){
            document.getElementById('start_button').style.display = "inline";
            document.getElementById('draw_button').disabled = true;
            document.getElementById("users").style.display = "none";
            var element = document.getElementById(last_card);
            element.style.display = "none";
            hideAll();
            disableAll();
        });

        socket.on("start",function(data){
            document.getElementById('start_button').style.display = "none";
            document.getElementById('draw_button').disabled = false;
            document.getElementById("users").style.display = "block";
            enableAll();
            users = data.users
        });

        if (getCookie("Username") == null){
            document.cookie = "Username="+prompt("Username")+";";
        }


    </script>
    <style>
    @font-face {font-family:Cabin ; src:url('Cabin-Bold.ttf')}
    @media (prefers-color-scheme: dark) {
        body {
            background-color: #333333;
            color: #ffffff;
        }
    }
    @media (prefers-color-scheme: light) {
        body {
            background-color: #ffffff;
            color: #000000;
        }
    }
    body {
        height: 100%;
        width: 100%;
        margin: 0px;
        font-family:Cabin;
        font-size: 20px;
        text-align:center;
        justify-content:center;
    }
    .ui_button {
        background-color: highlight;
        font-family:Cabin;
        color: white;
        border: none;
        border-radius: 10px;
        padding: 5px;
        padding-left: 10px;
        padding-right: 10px;
        transition: scale 0.05s ease-out;
    }
    .ui_button:hover:enabled {
        scale:1.1;
    }
    .ui_button:disabled {
        color:lightgray;
    }
    .card {
        position: static;
        border-radius: 14px;
        padding: 0px;
        margin: 2px;
        border-width: 2px;
        border-color: black;
        border-style: solid;
        transition: margin 0.1s ease-out;
    }
    .card:enabled:hover {
        background-color:black;
        margin-top: -10px;
        margin-bottom: 14px;

    }
    </style>
    
    <button id="start_button" class="ui_button" onclick="socket.emit('start');">Start</button>
    <p id="users" style="display:inline;"></p>
    <br>
    <div id="leaderboard" style="text-align:right; margin-right:10px;"></div>
    <br style="line-height: 200px;">
    <br>
    <button id="draw_button" class="ui_button" onclick="drawCard()">Draw <span id="draw_counter"></span></button>
    <br>
    <div style="display: flex; flex-wrap:wrap;justify-content:center;">
    """
    for card in game.all_cards:
        form += f"""
<button name="{card.get_description()}" onclick="useCard({card.id})" id="{card.id}" class="card" style="background:{card.color.value}; display: none"><img src="{card.get_image()}" alt="{card.get_description()}" style="width: 66px;height: 100px;"></button>"""
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
    update_leaderboard()
    emit("start", {"users": game.users}, broadcast=True)
    for user_id in game.cards.keys():
        for i in range(10):
            draw_card(user_id)
    for i in range(len(game.draw_pile)):
        if game.draw_pile[i].card_type.value < 10:
            game.discard_pile.append(game.draw_pile.pop(i))
            break
    emit("card_used", {"id": game.discard_pile[-1].id}, broadcast=True)
    set_user(request.sid)


@socketio.on("draw_card")
def handle_draw_card():
    user_id = request.sid
    for i in range(max(1, game.draw_number)):
        draw_card(user_id)
    reset_draw()


@socketio.on("card_use")
def handle_card_use(json):
    user_id = request.sid
    if can_play_card(user_id, json["id"]):
        emit("card_removed", json)
        emit("card_used", json, broadcast=True)
        play_card(user_id, json["id"])

@socketio.on("connect")
def handle_connect():
    user_id = request.sid
    if not user_id:
        return
    game.cards[user_id] = []
    game.leaderboard[user_id] = 0
    game.users[user_id] = request.cookies.get("Username","Unknown")
    # for i in range(10):
        # game.cards[user_id].append(game.draw_pile.pop())
    print(f"[USER CONNECTED] username={game.users[user_id]}, ip={request.remote_addr}, {user_id=}, sid={request.sid}")

@app.route("/", methods=["GET"])
def index():
    resp = make_response()
    resp.set_data(render_cards())
    return resp


if __name__ == "__main__":
    socketio.run(app=app, host="::", port=8080, debug=True, use_reloader=True, log_output=True)
