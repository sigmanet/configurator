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

@application.route("/postchange", methods = ['GET', 'POST'])
def postChange():
    data = {}
    data['foo'] = 'foo'
    return "<H1>got to here</H1>"
    data['vlan_id'] = request.form['rtn_vlan']
    data['intf_id'] = request.form['rtn_ports'].split(",")
    data['intf_desc'] = request.form['desc']
    data['switch_ip'] = request.form['rtn_switchip']

    result = switchconfig.conf_intfs(data)
    return render_template('base.html',
                           pagetitle="Config Confirmation",
                           leadtext="Congratulations! Your Interfaces Have Been Configured!",
                           content="<p>The following configuration was applied to switch %s based on your reqest</p><br><pre>%s</pre>" % (request.form['rtn_switchip'], result))


@application.route("/auditlog")
def auditLog():
    return render_template('base.html',
                           pagetitle="audit log",
                           leadtext="Log of Configuration Changes",
                           content=getAuditLogContent())


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
    rtn='''<form id="form1" action="/postchange" method="post"><input type="hidden" id="rtn_switchip"></input><input type="hidden" id="rtn_vlan"></input><input type="hidden" id="rtn_ports"></input><div class="form-group"><select multiple="multiple" size="10" name="duallistbox_demo1[]">'''
    
    interfaces = switchconfig.get_intfs(ipaddr)
    for intf in interfaces:
        rtn+='<option value="%s">%s</option>' % (intf, intf)

    rtn+='</select><br><br><div class="dropdown"><button class="btn btn-primary dropdown-toggle pull-left btn-block" type="button" data-toggle="dropdown">Choose a VLAN<span class="caret"></span></button><ul class="dropdown-menu">'
    vlans = switchconfig.get_vlans(ipaddr)
    #list of lists
    ddjs = ""
    for vlan in vlans:
        rtn += "<li><a href='#' id='vlan%s'>%s</a></li>" % (vlan[0], vlan[1])
        ddjs += '$("#vlan%s").click(function(e){$("#rtn_vlan").val(%s); e.preventDefault(); }); ' % (vlan[0], vlan[0])
    
    rtn += '''</ul></div><br><br><label for="desc">Interface Description:</label><input type="text" class="form-control" name="desc" id="desc"></input></div><br><br><button type="submit" class="btn btn-default btn-block">Submit data</button></form><script>
            var demo1 = $('select[name="duallistbox_demo1[]"]').bootstrapDualListbox();
$("#form1").submit(function() {
      $('#rtn_switchip').val(getParameterByName('ip'));
      $('#rtn_ports').val($('[name="duallistbox_demo1[]"]').val());
      if($('#rtn_ports').val().length < 3){alert('you must select an interface'); return false;}
      if($("#rtn_vlan").val() === null || $("#rtn_vlan").val() == ""){ alert('you must select a vlan'); return false;}
      if($('#desc').val() === null || $('#desc').val() == ""){alert('you must enter a description for the interface(s)'); return false;}
      return;
    });
'''
    rtn += ddjs
    rtn += "</script>"
    return rtn

def getAuditLogContent():
    rtn = '<table class="table table-striped"><thead></thead><tbody>'
    entries = switchconfig.get_log()
    for entry in entries:
        rtn += "<tr><td class='text-left'>%s</td></tr>" % (entry)
    rtn += "</tbody></table>"
    return rtn


if __name__ == "__main__":
    application.debug = True
    application.run(host='0.0.0.0')
