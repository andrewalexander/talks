package main

import (
	"bytes"
	"encoding/json"
	"flag"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"os/exec"
	"strconv"
	"strings"
	"text/template"
)

type ServerInfo struct {
	Port        int
	URL         string
	ContainerId string
	Name        string
	Error       string
}

var clientMap map[string][]ServerInfo
var instanceUrl string

func SaveClient(eid string, port int, container_id string, firstName string) {
	c := ServerInfo{}
	c.Port = port
	c.ContainerId = container_id
	c.Name = firstName
	c.URL = instanceUrl
	clientMap[eid] = append(clientMap[eid], c)
	writeFile(clientMap)
}

func writeFile(clientMap map[string][]ServerInfo) {
	outFile, _ := json.Marshal(clientMap)
	err := ioutil.WriteFile("client-map.json", outFile, 0644)
	if err != nil {
		fmt.Println("Couldn't save map to file. Current contents: %+v", clientMap)
	}
}

func init() {
	// see if file exists, if it does - load into clients; else leave it at zero-value
	clientMap = make(map[string][]ServerInfo)
	if _, err := os.Stat("client-map.json"); !os.IsNotExist(err) {
		raw, err := ioutil.ReadFile("client-map.json")
		if err != nil {
			log.Fatal(err)
		}
		json.Unmarshal(raw, &clientMap)
	}
}

func runCommand(command string) (response string, err error) {
	var out bytes.Buffer
	cmd := exec.Command("sh", "-c", command)
	cmd.Stdout = &out
	err = cmd.Run()
	if err != nil {
		return "", err
	}
	return strings.TrimSpace(out.String()), nil
}

func getContainerCount() (count int, err error) {
	command := "/usr/bin/docker ps -a | wc | awk '{print $1}'"
	numContainers, err := runCommand(command)
	if err != nil {
		return 0, err
	}
	count, err = strconv.Atoi(numContainers)
	if err != nil {
		return 0, err
	}
	return count, nil
}

func launchDockerContainer() (port int, container_id string, err error) {
	offset, err := getContainerCount()
	if err != nil {
		return 0, "", err
	}
	port = 3000 + offset
	fmt.Printf("Launching container with port: %d\n", port)
	command := fmt.Sprintf("/usr/bin/docker run -d -p %d:3000 bkimminich/juice-shop", port)
	container_id, err = runCommand(command)
	return port, container_id, nil
}

func homePage(w http.ResponseWriter, r *http.Request) {
	fmt.Printf("%s: \"/\"\n", r.Method)
	info := []ServerInfo{}
	if r.Method == "GET" {
		t := template.Must(template.ParseGlob("templates/*"))
		t.ExecuteTemplate(w, "index", info)
	}
}

func requestServer(w http.ResponseWriter, r *http.Request) {
	fmt.Printf("%s: \"/request_server\"\n", r.Method) //get request method
	if r.Method == "GET" {
		http.Redirect(w, r, "/", 301)
	} else {
		r.ParseForm()

		// pre-parse response for error reporting
		t := template.Must(template.ParseGlob("templates/*"))

		firstName := template.HTMLEscapeString(r.Form.Get("firstName"))
		eid := template.HTMLEscapeString(r.Form.Get("eid"))
		// launch docker container, get port
		port, container_id, err := launchDockerContainer()
		if err != nil {
			p := []ServerInfo{}
			p[0] = ServerInfo{}
			p[0].Error = fmt.Sprintf("Could not launch Docker container. Please let Admin know.")
			t.Execute(w, p)
		}
		SaveClient(eid, port, container_id, firstName)

		// redirect to index with new info substituted
		t.ExecuteTemplate(w, "index", clientMap[eid])
	}
}

func findServer(w http.ResponseWriter, r *http.Request) {
	fmt.Printf("%s: \"/find_server\"\n", r.Method)
	if r.Method == "GET" {
		http.Redirect(w, r, "/", 301)
	} else {
		r.ParseForm()
		eid := template.HTMLEscapeString(r.Form.Get("eid"))
		info := clientMap[eid]
		if len(info) == 0 {
			i := ServerInfo{}
			i.Error = "No containers"
			info = append(info, i)
		}
		t := template.Must(template.ParseGlob("templates/*"))
		t.ExecuteTemplate(w, "index", info)
	}

}

func killServer(w http.ResponseWriter, r *http.Request) {
	fmt.Printf("%s: \"/kill_server\"\n", r.Method)
	if r.Method == "GET" {
		http.Redirect(w, r, "/", 301)
	} else {
		r.ParseForm()
		eid := template.HTMLEscapeString(r.Form.Get("eid"))
		c := clientMap[eid]
		errors := []ServerInfo{}
		for _, client := range c {
			container := client.ContainerId
			command := fmt.Sprintf("docker kill %s && docker rm %s", container, container)
			_, err := runCommand(command)
			if err != nil {
				i := ServerInfo{}
				i.Error = "Could not delete container."
				errors = append(errors, i)
			}
		}
		if len(errors) > 0 {
			t := template.Must(template.ParseGlob("templates/*"))
			t.ExecuteTemplate(w, "index", errors)
		} else {
			delete(clientMap, eid)
			writeFile(clientMap)
		}

		t := template.Must(template.ParseGlob("templates/*"))
		t.ExecuteTemplate(w, "index", nil)
	}

}

func main() {
	flag.StringVar(&instanceUrl, "url", "10.206.2.123", "IP address or CNAME of Server")
	http.HandleFunc("/", homePage) // setting router rule
	http.HandleFunc("/request_server", requestServer)
	http.HandleFunc("/find_server", findServer)
	http.HandleFunc("/kill_servers", killServer)
	err := http.ListenAndServe(":9090", nil) // setting listening port
	if err != nil {
		log.Fatal("ListenAndServe: ", err)
	}
}
