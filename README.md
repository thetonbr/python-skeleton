## example

### Requirements

- Linux or macOS
- Make
- Git
- Docker +19.03
- Docker Compose +3.8
- Bash +4
- GNU sed
- Python +3.8

### Usage

```shell
Usage:
  make <target> [local=0] [deploy=0] [services=1] [consumers=0]

Targets:
  build                     Builds env files, networks, volumes and container images.
  deps                      Installs container dependencies.
  deps-local                Installs application dependencies locally.
  prepare                   Starts containers.
  prepare-services          Starts services containers.
  prepare-local             Starts application process locally.
  stop                      Stops containers.
  validate-docker-compose   Validates containers config.
  security-code-analysis    Executes security code analysis.
  static-code-analysis      Executes static code analysis.
  unit-tests                Executes unit tests.
  integration-tests         Executes integration tests.
  functional-tests          Executes functional tests.
  functional-wip-tests      Executes functional wip tests.
  deploy                    Deploy images.
  clean                     Cleans containers, volumes and networks.
```

### Recommendations

- Slack
- Authy
- Miro
- Notion
- IntelliJ IDEA or Visual Studio Code
- Homebrew (macOS's users)
- Virtual Box
- Docker Machine
- Dinghy (macOS's users)

### Code Styles

#### Analyzers

- See [./tests/.pylintrc](https://docs.pylint.org/)
- See [./tests/mypy.ini](https://mypy.readthedocs.io/)
- See [./tests/.bandit](https://bandit.readthedocs.io)
- See [./tests/licenses.ini](https://github.com/dhatim/python-license-check)

#### Standards

- See [JSON:API 1.0](https://jsonapi.org/format)
> example
```sh
GET /<resource>/<id> HTTP/1.1
Accept: application/json

{
   "data":{
      "type":"<resource>",
      "id":"<id>",
      "attributes":{
         "<field>":"<value>"
      }
   },
   "meta":{}
}

GET /<resource> HTTP/1.1
Accept: application/json

{
   "data":[
      {
         "type":"<resource>",
         "id":"<id>",
         "attributes":{
            "<field>":"<value>"
         },
         "meta":{}
      },
      {
         "type":"<resource>",
         "id":"<id>",
         "attributes":{
            "<field>":"<value>"
         }
      }
   ],
   "meta":{}
}

POST /<resource> HTTP/1.1
Accept: application/json

{
   "data":{
      "type":"<resource>",
      "id":"<id>",
      "attributes":{
         "<field>":"<value>"
      }
   },
   "meta":{}
}

POST /<resource> HTTP/1.1
Accept: application/json

{
   "errors":[
      {
         "id":"<error_id>",
         "status":"<http_status_code>",
         "code":"<custom_code>",
         "title":"<string>",
         "detail":"<string>",
         "meta":{}
      }
   ]
}
```
- See [AsyncAPI 2.0](https://www.asyncapi.com/docs/specifications/2.0.0)
```sh
# Vhost

Name: example

# Exchanges

Name: "example.<service>"
Type: "topic"
Features:
	durable: true

# Queues

Name: "example.<service>.<aggregate>.<message_name>"
Type: "topic"
Features:
	durable: true

# Bindings

Exchange: "example.<service>"
Queue: "example.<service>.<aggregate>.<message_name>"
Name: "<message_name>"

# Messages

Exchange: "example.<service>"
Routing key: "<message_name>"
Properties:
	timestamp: <timestamp>
	message_id: "<uuid>"
	delivery_mode: 2
	content_type: "application/json"
Body:
	{
		"id": "<uuid>",
		"type": "<event|command>",
		"occurredOn": <timestamp>,
		"attributes": {
			"key": "value"
		},
		"meta": {
			"message": "example.<service>.<message_name>"
		}
	}
```

### How to set up macOS's user recommendations?

```bash
# Install Homebrew (if you don't have it)
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

# Install Homebrew's recipes
brew tap homebrew/cask-versions homebrew/services codekitchen/dinghy 

# Install Virtual Box (if you don't have it)
brew cask install virtualbox virtualbox-extension-pack

# Install Docker and Docker Compose (if you don't have them)
brew install docker docker-compose 

# Install Docker Machine and Dinghy
brew install docker-machine dinghy

# Setup macOS NFS's config (free to change it)
{
 echo 'nfs.lockd.port=951'
 echo 'nfs.server.mount.port=952'
 echo 'nfs.server.port=2049'
 echo 'nfs.server.rquota.port=953'
 echo 'nfs.statd.port=954'
} >> /etc/nfs.conf

# Setup Dinghy's config (free to change it)
{
 echo '---'
 echo ':preferences:'
 echo '  :unfs_disabled: false'
 echo '  :proxy_disabled: true'
 echo '  :dns_disabled: false'
 echo '  :fsevents_disabled: false'
 echo '  :machine_name: default'
 echo '  :create:'
 echo '    provider: virtualbox'
 echo '    memory: 8192'
 echo '    cpus: 4'
 echo '    disk: 32768'
} > ~/.dinghy/preferences.yml

# Create Docker Machine with Dinghy
dinghy create

# Update bash profile to load Dinghy's Docker Machine environments automatically
echo "eval $(dinghy env)" >> ~/.bash_profile
source ~/.bash_profile

# Update zsh profile to load Dinghy's Docker Machine environments automatically (if you have it)
echo "eval $(dinghy env)" >> ~/.zshrc
source ~/.zshrc

# Configure loopback Docker Machine's ip
ifconfig lo0 alias 10.254.254.254

# Execute Docker Machine
dinghy up
```

### What apps and tools recommended for macOS's user?

```sh
brew cask install \
    slack \
    authy \
    notion \
    google-chrome \
    mongodb-compass \
    jetbrains-toolbox \
    visual-studio-code \
    postman \
    deepl \
    miro-formerly-realtimeboard

brew install \
    mas \ # Mac App Store CLI
    htop \
    watch \
    nmap \
    telnet \
    tree \
    wget \
    bash \
    zsh

mas install \
    595191960 \ # CopyClip
    1081413713 # GIF Brewery 3
```
