{{ define "index" }}
<html>
<head>
    <title></title>
    <style>
    body {
        font-family: helvetica;
        background-color: aliceblue;
    }
    h2 {
        margin: 0;
        margin-bottom: 10px;
        text-align: center;
        font-weight: normal;
    }
    .main {
        max-width: 700px;
        min-width: 400px;
        margin: 10px auto;
        padding: 20px;
        background-color: white;
        padding-bottom: 40px;
    }
    .form-group {
        display: flex;
        flex-direction: column;
        width: 50%;
        min-width: 360px;
        margin: 0 auto;
        margin-top: 6px;
        margin-bottom: 30px;
    }
    .form-group > * {
        margin-bottom: 5px;
    }
    .form-group input[type="submit"] {
        align-self: flex-start;
        outline: none;
        border: none;
        padding: 8px;
        color: white;
        align-self: flex-end;
        cursor: pointer;
        background-color: cornflowerblue;
    }
    label {
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        width: 100%;
        color: #666;
    }
    input[type="text"] {
        max-width: 400px;
        width: 100%;
        padding: 8px;
    }
    .error {
        color: white;
        background-color: tomato;
        padding: 8px;
        text-align: center;
    }
    .info {
        text-align: center;
        color: #555;
        font-size: 0.97em;
    }
    input[type="submit"].kill {
        background-color: tomato;
    }
    input[type="submit"]:hover {
        opacity: 0.9;
    }
    .server {
        font-family: monospace;
        margin: 10px;
        display: flex;
        justify-content: space-between;
    }
    </style>
</head>
<body>
    <div class="main">
        <h2>Request a container</h2>
        <form action="/request_server" method="post">
            <div class="form-group">
              <label><input type="text" placeholder="Name" name="firstName"></label>
              <label><input type="text" name="eid" required="" placeholder="EID"></label>
              <input type="submit" value="Request Server">
            </div>
        </form>
        <h2>Lookup container information</h2>
        <form action="/find_server" method="post">
            <div class="form-group">
                <label><input type="text" name="eid" required="" placeholder="EID"></label>
                <input type="submit" value="Look Up Server">
            </div>
        </form>
        <h2>Kill containers</h2>
        <div class="info">Enter your EID to kill all containers you have launched (be nice...)</div>
        <form action="/kill_servers" method="post">
            <div class="form-group">
                <label><input type="text" name="eid" required="" placeholder="EID"></label>
                <input type="submit" value="Kill Container" class="kill">
            </div>
        </form>
        <h2>Your Server Information</h2>
        {{range $index, $elem := .}}
            {{ if $elem.URL }}
                <div class="server">
                    <b>{{$elem.ContainerId}}</b> <span>Server URL: <a href="http://{{$elem.URL}}:{{$elem.Port}}" target="_blank">{{$elem.URL}}:{{$elem.Port}}</a></span>
                </div>
            {{ else if $elem.Error }}
                <div class="server error">Error encountered: {{$elem.Error}}</div>
            {{ else }}
                No containers found. Please create a container.
            {{end}}
        {{ else }}
            <div class="info">Either create a server or lookup your existing server.</div>
        {{ end }}
    </div>
</body>
</html>
{{ end }}
