# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant::Config.run do |config|
  # All Vagrant configuration is done here. The most common configuration
  # options are documented and commented below. For a complete reference,
  # please see the online documentation at vagrantup.com.

  # Every Vagrant virtual environment requires a box to build off of.
  config.vm.box = "ubuntu_10_04"

  # The url from where the 'config.vm.box' box will be fetched if it
  # doesn't already exist on the user's system.
  # config.vm.box_url = "http://domain.com/path/to/above.box"

  # Share an additional folder to the guest VM. The first argument is
  # an identifier, the second is the path on the guest to mount the
  # folder, and the third is the path on the host to the actual folder.
  config.vm.share_folder "v-cloudfoundry", "/cloudfoundry", "cloudfoundry"

  # Main Cloud Foundry node
  config.vm.define :main do |main_config|

    # Customize memory size
    main_config.vm.customize ["modifyvm", :id, "--memory", 384]

    # Assign this VM to a host-only network IP, allowing you to access it
    # via the IP. Host-only networks can talk to the host machine as well as
    # any other machines on the same network, but cannot be accessed (through this
    # network interface) by any external networks.
    main_config.vm.network :hostonly, "192.168.33.10"

    # Forward a port from the guest to the host, which allows for outside
    # computers to access the VM, whereas host only networking does not.
    main_config.vm.forward_port 80, 8888
  end

  # App node #1
  config.vm.define :app1 do |app1_config|
    app1_config.vm.customize ["modifyvm", :id, "--memory", 256]
    app1_config.vm.network :hostonly, "192.168.33.101"
  end

  # App node #2
  config.vm.define :app2 do |app2_config|
    app2_config.vm.customize ["modifyvm", :id, "--memory", 256]
    app2_config.vm.network :hostonly, "192.168.33.102"
  end

end
