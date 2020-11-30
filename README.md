# python-skeleton

python-skeleton is a project based on best practices to start API and CLI apps with Python.

### Usage (Ubuntu and macOS)

```shell
make help

sh pyscript.sh help
```

### Usage (Windows)

```shell
docker-compose run --rm --entrypoint="sh pyscript.sh help" app
```

### Requirements (macOS)

```shell
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

brew tap homebrew/cask-versions && brew tap homebrew/services && brew tap codekitchen/dinghy 
brew update

brew install git make wget python
pip3 install tox
brew cask install google-chrome mongodb-compass jetbrains-toolbox virtualbox virtualbox-extension-pack

# Install Dinghy to use faster Docker or install Desktop version here https://hub.docker.com/editions/community/docker-ce-desktop-mac/

brew install docker docker-compose docker-machine dinghy

echo "nfs.lockd.port=951\nnfs.server.mount.port=952\nnfs.server.port=2049\nnfs.server.rquota.port=953\nnfs.statd.port=954" >> /etc/nfs.conf
echo "---\n:preferences:\n  :unfs_disabled: false\n  :proxy_disabled: true\n  :dns_disabled: false\n  :fsevents_disabled: false\n  :machine_name: default\n  :create:\n    provider: virtualbox\n    memory: 8192\n    cpus: 4\n    disk: 65564" > ~/.dinghy/preferences.yml

dinghy create

echo "eval $(dinghy env)" >> ~/.bash_profile && source ~/.bash_profile
# echo "eval $(dinghy env)" >> ~/.zshrc && source ~/.zshrc
ifconfig lo0 alias 10.254.254.254

mkdir -p ~/Developer
git clone git@github.com:ticdenis/python-skeleton.git ~/Developer/project
cd ~/Developer/project

# Install PyCharm Community with jetbrains-toolbox application
  # Setup Python interpeter in "Preferences | Project: <project> | Python Interpreter"
  # Set Continuation indent" to "4" in "Preferences | Editor | Code Style | Python | Tabs and Indents"
  # Mark Sort imported names in "from" imports in "Preferences | Editor | Code Style | Python | Imports"
  # Install "Toml" and "pytest imp" plugins in "Preferences | Plugins"
  # Mark test runner "pytest" in "Preferences | Tools | Python Integrated Tools"
  # Add ".env.local" file in "Run/Debug Configurations | Templates | Python tests | pytest | EnvFile"
```

### Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

### License

[MIT](https://github.com/ticdenis/python-skeleton/blob/master/LICENSE)
