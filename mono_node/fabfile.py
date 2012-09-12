from fabric.api import run,env,cd, sudo
from fabtools.deb import update_index, upgrade
from fabtools.openvz import guest
from fabtools import require


env.hosts = ['root@services.server-2.mycozycloud.com']
VM = '124'
DOMAIN ='cf-test.mycozycloud.com'


def install():
    with guest(VM):
        update()
        get_CF()
        

def update():
    """
    Update vm before installing
    """
    update_index()
    upgrade()

def get_CF():
    sudo('apache2ctl stop')
    require.deb.packages(['git-core'])
    with cd('/root/'):
        sudo('git clone https://github.com/cloudfoundry/vcap.git')
        
