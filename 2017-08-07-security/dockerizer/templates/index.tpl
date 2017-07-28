{{ define "index" }}
<html>
    <head>
    <title></title>
    </head>
    <body>
    	<h2>Request a container</h2>
        <form action="/request_server" method="post">
            Name:<input type="text" name="firstName">
            EID:<input type="text" name="eid" required> 
            <input type="submit" value="Request Server">
        </form>
    	<h2>Lookup container information</h2>
        <form action="/find_server" method="post">
            EID:<input type="text" name="eid" required>
            <input type="submit" value="Look Up Server">
        </form>
    	<h2>Kill containers</h2>
	Enter your EID to kill all containers you have launched (be nice...)
        <form action="/kill_servers" method="post">
	    EID:<input type="text" name="eid" required> 
            <input type="submit" value="Kill Container">
        </form>
	<h2>Your Server Information:</h2>
	<p>
	{{range $index, $elem := .}}
		{{ if $elem.URL }}
			<h4>Server {{$index}}:</h4>
			Server URL: {{$elem.URL}}:{{$elem.Port}} <br>
			Container ID: {{$elem.ContainerId}} <br>
		{{ else if $elem.Error }}
			Error encountered: {{$elem.Error}}

		{{ else }}
			No containers found. Please create a container.
		{{end}}
	{{ else }}
		Either create a server or lookup your existing server.
	{{ end }}
	</p>

    </body>
</html>
{{ end }}
