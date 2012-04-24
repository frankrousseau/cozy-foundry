import os.path

from fabric.api import *
from fabtools import require
import fabtools


@task
def vagrant():
    """
    Setup vagrant VM as the remote host
    """
    with settings(hide('running')):
        output = local('vagrant ssh-config', capture=True)

    config = {}
    for line in output.splitlines()[1:]:
        key, value = line.strip().split(' ', 2)
        config[key] = value

    user = config['User']
    hostname = config['HostName']
    port = config['Port']

    env['host_string'] = "%s@%s:%s" % (user, hostname, port)
    env['user'] = user
    env['key_filename'] = config['IdentityFile']
    env['disable_known_hosts'] = True


@task
def install(config='cozy.yml'):
    """
    Setup a Cozy-flavored CF environment
    """
    # Clone the vcap repo
    if not os.path.exists('vcap'):
        local('git clone git://github.com/cloudfoundry/vcap.git')

    # Pull latest changes
    with lcd('vcap'):
        local('git pull')

    # Package the setup tools
    local('tar czf dev_setup.tar.gz vcap/dev_setup')

    # Upload the setup tools to the remote host
    put('dev_setup.tar.gz')
    if fabtools.files.is_dir('dev_setup'):
        run('rm -rf dev_setup')
    run('tar xzf dev_setup.tar.gz --strip-components=1')

    # Upload config file
    put(config)

    # Run the setup
    with cd('dev_setup/bin'):
        options = ['-c ~/%s' % config]

        # Use vcap repo in Vagrant shared folder
        # if we're running inside a local VM
        if fabtools.files.is_file('/vagrant/vcap'):
            options.append('-r /vagrant/vcap')

        run('./vcap_dev_setup ' + ' '.join(options))

    # Disable chef-client daemon
    sudo('/etc/init.d/chef-client stop')
    sudo('update-rc.d -f chef-client remove')


@task
def start():
    """
    Start CF services
    """
    with prefix('source .cloudfoundry_deployment_profile'):
        run('cloudfoundry/vcap/dev_setup/bin/vcap_dev -n cozy start', pty=False)


@task
def stop():
    """
    Stop CF services
    """
    with prefix('source .cloudfoundry_deployment_profile'):
        run('cloudfoundry/vcap/dev_setup/bin/vcap_dev -n cozy stop', pty=False)


@task
def restart():
    """
    Restart CF services
    """
    with prefix('source .cloudfoundry_deployment_profile'):
        run('cloudfoundry/vcap/dev_setup/bin/vcap_dev -n cozy restart', pty=False)


@task
def tail():
    """
    Tail CF logs
    """
    with prefix('source .cloudfoundry_deployment_profile'):
        run('cloudfoundry/vcap/dev_setup/bin/vcap_dev -n cozy tail')


@task
def status():
    """
    Check the status of CF services
    """
    with prefix('source .cloudfoundry_deployment_profile'):
        run('cloudfoundry/vcap/dev_setup/bin/vcap_dev -n cozy status')


@task
def info():
    with prefix('source .cloudfoundry_deployment_profile'):
        run('vmc info')
