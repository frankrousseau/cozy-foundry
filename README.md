Requirements
------------

We use [Fabric](http://fabfile.org/) and [fabtools](http://pypi.python.org/pypi/fabtools) to run commands on the VM. To install these tools system-wide on an Ubuntu box:

    $ sudo apt-get install python-pip
    $ sudo pip install fabtools

Installing on a Vagrant VM
--------------------------

We use [Vagrant](http://vagrantup.com/) to manage [Virtualbox](https://www.virtualbox.org/) VMs.

Spin up a 512MB virtual machine with Ubuntu 10.04 (64-bit):

    $ vagrant up

Install a minimal Cozy-flavored Cloud Foundry environment:

    $ fab vagrant install
    $ fab vagrant start

Install the command-line client:

    $ sudo gem install vmc

Setup our VM as our target:

    $ vmc target http://api.vcap.me:8080/

Register a user account:

    $ vmc register

Deploy an example Node.js app (do not forget to remove the port number in the URL):

    $ cd sample-apps/hello-node
    $ vmc push --runtime=node06
    Would you like to deploy from the current directory? [Yn]: 
    Application Name: hello-node
    Application Deployed URL [hello-node.vcap.me:8888]: hello-node.vcap.me
    Detected a Node.js Application, is this correct? [Yn]: 
    Memory Reservation (64M, 128M, 256M, 512M, 1G, 2G) [64M]: 
    Would you like to bind any services to 'hello'? [yN]: 
    Creating Application: OK
    Uploading Application:
      Checking for available resources: OK
      Packing application: OK
      Uploading (1K): OK   
    Push Status: OK
    Staging Application: OK
    Starting Application: OK

Let's check that the application is running:

    $ curl http://hello-node.vcap.me:8888
    Hello world

Now another Node.js app, but using MongoDB:

    $ cd sample-apps/mongo-node
    $ vmc push --runtime=node06
    Would you like to deploy from the current directory? [Yn]: 
    Application Name: mongo
    Application Deployed URL [mongo.vcap.me:8888]: mongo.vcap.me
    Detected a Node.js Application, is this correct? [Yn]: 
    Memory Reservation (64M, 128M, 256M, 512M, 1G) [64M]: 
    Creating Application: OK
    Would you like to bind any services to 'mongo'? [yN]: y
    The following system services are available
    1: mongodb
    Please select one you wish to provision: 1
    Specify the name of the service [mongodb-5a9b0]: 
    Creating Service: OK
    Binding Service [mongodb-5a9b0]: OK
    Uploading Application:
      Checking for available resources: OK
      Packing application: OK
      Uploading (1K): OK
    Push Status: OK
    Staging Application: OK
    Starting Application: OK

Let's check that the application is running by doing a few requests:

    $ curl http://mongo.vcap.me:8888
    $ curl http://mongo.vcap.me:8888
    $ curl http://mongo.vcap.me:8888/history
