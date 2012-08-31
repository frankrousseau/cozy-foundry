import os.path
import re

from fabric.api import *
from fabtools import require
import fabtools


NODE_LIST = [
    {
        'name': 'main',
        'config': 'cozy-main.yml',
        'deployment': 'cozy',
    },
    {
        'name': 'app1',
        'config': 'cozy-app.yml',
        'deployment': 'cozy-app',
    },
    {
        'name': 'app2',
        'config': 'cozy-app.yml',
        'deployment': 'cozy-app',
    },
]


def ssh_config(name):
    """
    Get the SSH parameters for this vagrant VM
    """
    with settings(hide('running')):
        output = local('vagrant ssh-config %s' % name, capture=True)

    config = {}
    for line in output.splitlines()[1:]:
        key, value = line.strip().split(' ', 2)
        config[key] = value
    return config


def vagrant(name, *args, **kwargs):
    """
    Fabric context manager that sets a vagrant VM
    as the remote host
    """
    config = ssh_config(name)

    user = config['User']
    hostname = config['HostName']
    port = config['Port']

    kwargs['host_string'] = "%s@%s:%s" % (user, hostname, port)
    kwargs['user'] = user
    kwargs['key_filename'] = config['IdentityFile']
    kwargs['disable_known_hosts'] = True

    return settings(*args, **kwargs)


def init_cloud_foundry():
    """
    Setup local copies of CF repositories
    """

    local('mkdir -p cloudfoundry')

    for repo in ['vcap', 'cloud_controller', 'dea', 'router', 'stager']:

        # Clone repo
        if not os.path.exists('cloudfoundry/%s' % repo):
            local('git clone git://github.com/cloudfoundry/%s.git cloudfoundry/%s' % (repo, repo))

        # Pull latest changes
        with lcd('cloudfoundry/%s' % repo):
            local('git submodule update --init')
            local('git pull')

    # Package the setup tools
    with lcd('cloudfoundry'):
        local('tar czf dev_setup.tar.gz vcap/dev_setup')


def setup_cloud_foundry(config, extra_gems=None):
    """
    Setup Cloud Foundry on the remote host
    """

    # Upload the setup tools to the remote host
    put('cloudfoundry/dev_setup.tar.gz')
    if fabtools.files.is_dir('dev_setup'):
        run('rm -rf dev_setup')
    run('tar xzf dev_setup.tar.gz --strip-components=1')

    # Upload config file
    put(config)

    # Run the setup
    with cd('dev_setup/bin'):
        options = ['-c ~/%s' % os.path.basename(config)]

        # Use vcap repo in Vagrant shared folder
        # if we're running inside a local VM
        if fabtools.files.is_dir('/cloudfoundry/vcap'):
            options.append('-r /cloudfoundry')

        run('./vcap_dev_setup ' + ' '.join(options))

    # Install extra gems?
    if extra_gems:
        with prefix('source .cloudfoundry_deployment_profile'):
            for gem in extra_gems:
                run('gem install %s' % gem)

    # Disable chef-client daemon
    sudo('/etc/init.d/chef-client stop')
    sudo('update-rc.d -f chef-client remove')


@task
def setup():
    """
    Setup a Cozy-flavored CF environment
    """
    # Make a local copy of the CF repo
    init_cloud_foundry()

    # Spin up our VMs
    local('vagrant up')

    # Setup CF on each node
    for node in NODE_LIST:
        with vagrant(node['name']):
            setup_cloud_foundry(node['config'], node.get('gems'))


@task
def start():
    """
    Start CF services
    """
    for node in NODE_LIST:
        with vagrant(node['name']):
            with prefix('source .cloudfoundry_deployment_profile'):
                run('cloudfoundry/vcap/dev_setup/bin/vcap_dev -n %s start' % node['deployment'], pty=False)


@task
def stop():
    """
    Stop CF services
    """
    for node in NODE_LIST:
        with vagrant(node['name']):
            with prefix('source .cloudfoundry_deployment_profile'):
                run('cloudfoundry/vcap/dev_setup/bin/vcap_dev -n %s stop' % node['deployment'], pty=False)


@task
def restart():
    """
    Restart CF services
    """
    for node in NODE_LIST:
        with vagrant(node['name']):
            with prefix('source .cloudfoundry_deployment_profile'):
                run('cloudfoundry/vcap/dev_setup/bin/vcap_dev -n %s restart' % node['deployment'], pty=False)


@task
def tail():
    """
    Tail CF logs
    """
    for node in NODE_LIST:
        with vagrant(node['name']):
            with prefix('source .cloudfoundry_deployment_profile'):
                run('cloudfoundry/vcap/dev_setup/bin/vcap_dev -n %s tail' % node['deployment'])


@task
def status():
    """
    Check the status of CF services
    """
    for node in NODE_LIST:
        with vagrant(node['name']):
            with prefix('source .cloudfoundry_deployment_profile'):
                run('cloudfoundry/vcap/dev_setup/bin/vcap_dev -n %s status' % node['deployment'])


@task
def info():
    for node in NODE_LIST:
        with vagrant(node['name']):
            with prefix('source .cloudfoundry_deployment_profile'):
                run('vmc info')
