from flask import Flask, render_template
application = Flask(__name__)

@application.route("/")
def hello():
    return "<h1 style='color:blue'>Hello There!</h1>"

@application.route("/pickswitch")
def pickSwitch():
    return render_template('base.html',
                           pagetitle="choose a switch",
                           leadtext="choose a switch to configure",
                           content="foobar")
    

if __name__ == "__main__":
    application.debug = True
    application.run(host='0.0.0.0')
