from flask import Flask, render_template, redirect, request
import switchconfig
application = Flask(__name__)

@application.route("/")
def hello():
    return redirect("/pickswitch", code=302)

@application.route("/pickswitch")
def pickSwitch():
    return render_template('base.html',
                           pagetitle="choose a switch",
                           leadtext="choose a switch to configure",
                           content=getPickSwitchContent())

@application.route("/pickports")
def pickPorts():
    ip = request.args.get('ip')
    return render_template('base.html',
                           pagetitle="choose ports",
                           leadtext="choose ports to configure",
                           content=getPickPortsContent(ip))

def getPickSwitchContent():
    rtn = '''<div class="dropdown">
  <button class="btn btn-primary dropdown-toggle btn-block" type="button" data-toggle="dropdown">Choose a switch
  <span class="caret"></span></button>
  <ul class="dropdown-menu">'''
    switches = switchconfig.get_switches()
    for switch in switches["switches"]:
        rtn += "<li><a href='/pickports?ip=%s'>%s</a></li>" % (switch['ip_addr'], switch['hostname'])
    rtn += '</ul></div>'
    return rtn

def getPickPortsContent(ipaddr):
    rtn='''<form id="form1" action="#" method="post"><div class="form-group"><select multiple="multiple" size="10" name="duallistbox_demo1[]">'''
    
    interfaces = switchconfig.get_intfs(ipaddr)
    for intf in interfaces:
        rtn+='<option value="%s">%s</option>' % (intf, intf)

    rtn+='</select><br><br><div class="dropdown"><button class="btn btn-primary dropdown-toggle pull-left btn-block" type="button" data-toggle="dropdown">Choose a VLAN<span class="caret"></span></button><ul class="dropdown-menu">'
    vlans = switchconfig.get_vlans(ipaddr)
    #list of lists
    for vlan in vlans:
        rtn += "<li><a href='/pickports?%s'>%s</a></li>" % (vlan[0], vlan[1])
    
    rtn += '''</ul></div><br><br><label for="desc">Interface Description:</label><input type="text" class="form-control" name="desc" id="desc"></input></div><br><br><button type="submit" class="btn btn-default btn-block">Submit data</button></form><script>
            var demo1 = $('select[name="duallistbox_demo1[]"]').bootstrapDualListbox();
</script>'''
    return rtn

if __name__ == "__main__":
    application.debug = True
    application.run(host='0.0.0.0')
